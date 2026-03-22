"""
Morning check-in.
Fast structured update of all manual metrics.
Runs at session open if no check-in today.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

import yaml

MEGAMIND = Path(__file__).parent.parent
STATE_FILE = MEGAMIND / "context" / "checkin_state.json"


def _load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def _save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def checked_in_today() -> bool:
    state = _load_state()
    return state.get("date") == str(date.today())


def get_checkin_questions() -> list[dict]:
    """
    Build check-in questions from quadrants.yaml.
    Only includes manual metrics (tracked_by: manual or absent).
    Returns list of {quadrant, metric, label, type, current, target, enum_values}.
    """
    path = MEGAMIND / "config" / "quadrants.yaml"
    cfg = yaml.safe_load(path.read_text())

    char_path = MEGAMIND / "context" / "character.json"
    char = json.loads(char_path.read_text()) if char_path.exists() else {}
    existing = char.get("stats", {})

    questions = []
    for qkey, qdef in cfg.get("quadrants", {}).items():
        for mkey, mdef in qdef.get("metrics", {}).items():
            # Skip only metrics whose MCP is actually connected (none yet)
            # When an MCP is wired, add it to LIVE_MCPS and it'll be skipped here
            LIVE_MCPS: set[str] = set()
            tracked_by = mdef.get("tracked_by", "manual")
            if tracked_by not in ("manual", "") and tracked_by in LIVE_MCPS:
                continue
            current = existing.get(qkey, {}).get("metrics", {}).get(mkey, mdef.get("current", 0))
            questions.append({
                "quadrant": qkey,
                "metric": mkey,
                "label": mdef.get("label", mkey),
                "type": mdef.get("type", "continuous"),
                "current": current,
                "target": mdef.get("target"),
                "enum_values": mdef.get("enum_values", []),
                "enum_scores": mdef.get("enum_scores", []),
                "unit": mdef.get("unit", ""),
            })
    return questions


def mark_checked_in() -> None:
    state = _load_state()
    state["date"] = str(date.today())
    state["completed_at"] = datetime.now().isoformat()
    _save_state(state)
