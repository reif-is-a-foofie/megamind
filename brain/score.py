"""
Scoring engine.
Reads config/quadrants.yaml, computes scores from current metric values,
writes context/character.json.

No hardcoded goals. The config is the game rules.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

CONFIG = Path(__file__).parent.parent / "config"
CONTEXT = Path(__file__).parent.parent / "context"
CONTEXT.mkdir(exist_ok=True)


def load_config() -> tuple[dict, dict]:
    player = yaml.safe_load((CONFIG / "player.yaml").read_text())
    quadrants = yaml.safe_load((CONFIG / "quadrants.yaml").read_text())
    return player, quadrants


def load_character() -> dict:
    path = CONTEXT / "character.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def score_metric(metric: dict) -> float:
    """Compute 0.0–1.0 score for a single metric."""
    mtype = metric.get("type", "continuous")
    current = metric.get("current", 0)
    target = metric.get("target", 1)

    if mtype == "boolean":
        return 1.0 if (current == 1 or current is True or current == "true") else 0.0

    if mtype == "enum":
        values = metric.get("enum_values", [])
        scores = metric.get("enum_scores", [])
        if current in values:
            idx = values.index(current)
            return scores[idx] if idx < len(scores) else 0.0
        return 0.0

    if mtype in ("continuous", "currency"):
        if target == 0:
            return 1.0 if current > 0 else 0.0
        return min(1.0, float(current) / float(target))

    return 0.0


def score_quadrant(metrics: dict) -> float:
    """Weighted sum of metric scores for a quadrant."""
    total = 0.0
    for key, m in metrics.items():
        weight = float(m.get("weight", 1.0 / len(metrics)))
        total += weight * score_metric(m)
    return round(total, 4)


def build_character(player: dict, quadrants: dict, existing: dict) -> dict:
    """
    Merge existing character state with current config.
    Config is the source of truth for targets and structure.
    Existing character is the source of truth for current values.
    """
    # Carry over current metric values from existing character
    existing_stats = existing.get("stats", {})

    stats = {}
    for qkey, qdef in quadrants.get("quadrants", {}).items():
        metrics = qdef.get("metrics", {})
        existing_metrics = existing_stats.get(qkey, {}).get("metrics", {})

        # Merge: keep existing current values, use config for everything else
        resolved_metrics = {}
        for mkey, mdef in metrics.items():
            m = dict(mdef)
            if mkey in existing_metrics:
                m["current"] = existing_metrics[mkey]
            resolved_metrics[mkey] = m

        stats[qkey] = {
            "label": qdef.get("label", qkey),
            "score": score_quadrant(resolved_metrics),
            "metrics": {k: v["current"] for k, v in resolved_metrics.items()},
            "targets": {k: v.get("target") for k, v in resolved_metrics.items()},
        }

    # Ventures (startup etc)
    ventures = {}
    existing_ventures = existing.get("ventures", {})
    for v in quadrants.get("ventures", []):
        vkey = v["key"]
        ev = existing_ventures.get(vkey, {})
        venture_metrics = {}
        for mkey, mdef in v.get("metrics", {}).items():
            m = dict(mdef)
            if mkey in ev:
                m["current"] = ev[mkey]
            venture_metrics[mkey] = m["current"]
        ventures[vkey] = {
            "label": v.get("label", vkey),
            "metrics": venture_metrics,
        }

    return {
        "character": {
            "name": player.get("name", "player"),
            "class": player.get("class", ""),
            "year": player.get("year", datetime.now().year),
        },
        "stats": stats,
        "ventures": ventures,
        "meta": {
            "last_updated": datetime.now().isoformat(),
            "session_count": existing.get("meta", {}).get("session_count", 0),
        },
    }


def update_metric(quadrant: str, metric: str, value: Any) -> dict:
    """
    Update a single metric value and recompute scores.
    Returns the updated character dict.
    """
    player, quadrants = load_config()
    character = load_character()

    # Drill into the right place
    stats = character.get("stats", {})
    if quadrant in stats and "metrics" in stats[quadrant]:
        stats[quadrant]["metrics"][metric] = value
        character["stats"] = stats

    # Rebuild to recompute scores
    # We need to merge current values back into config structure for scoring
    for qkey, qdef in quadrants.get("quadrants", {}).items():
        if qkey != quadrant:
            continue
        metrics = qdef.get("metrics", {})
        current_metrics = stats.get(qkey, {}).get("metrics", {})
        resolved = {}
        for mkey, mdef in metrics.items():
            m = dict(mdef)
            m["current"] = current_metrics.get(mkey, m.get("current", 0))
            resolved[mkey] = m
        character["stats"][qkey]["score"] = score_quadrant(resolved)

    character["meta"]["last_updated"] = datetime.now().isoformat()
    save_character(character)
    return character


def save_character(character: dict) -> None:
    path = CONTEXT / "character.json"
    path.write_text(json.dumps(character, indent=2))


def sync() -> dict:
    """Full sync: load config + existing state, rebuild, save, return."""
    player, quadrants = load_config()
    existing = load_character()
    character = build_character(player, quadrants, existing)
    save_character(character)
    return character


def get_scores() -> dict[str, float]:
    """Quick read of current quadrant scores."""
    char = load_character()
    return {
        qkey: qval.get("score", 0.0)
        for qkey, qval in char.get("stats", {}).items()
    }


if __name__ == "__main__":
    char = sync()
    print(json.dumps(char, indent=2))
