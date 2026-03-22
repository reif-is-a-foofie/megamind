"""
Megamind background thinking loop.
Runs once per hour via LaunchAgent (Mac) or cron.
Reads all context, reasons privately, updates its own model.
The player is not present. No output is shown to them.
Results are queued for next session.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

MEGAMIND = Path(__file__).parent.parent
sys.path.insert(0, str(MEGAMIND))

from dotenv import load_dotenv
load_dotenv(MEGAMIND / ".env")


# ─── Context loading ──────────────────────────────────────────

def load_context() -> dict:
    def read_json(p: Path) -> dict:
        try:
            return json.loads(p.read_text())
        except Exception:
            return {}

    def read_yaml(p: Path) -> dict:
        try:
            return yaml.safe_load(p.read_text()) or {}
        except Exception:
            return {}

    ctx = MEGAMIND / "context"
    cfg = MEGAMIND / "config"

    return {
        "player":       read_yaml(cfg / "player.yaml"),
        "quadrants":    read_yaml(cfg / "quadrants.yaml"),
        "character":    read_json(ctx / "character.json"),
        "tasks":        read_json(ctx / "tasks.json"),
        "causal_model": read_json(ctx / "causal_model.json"),
        "recent_thoughts": load_recent_thoughts(n=5),
    }


def load_recent_thoughts(n: int = 5) -> list[dict]:
    path = MEGAMIND / "context" / "thoughts.jsonl"
    if not path.exists():
        return []
    lines = path.read_text().strip().splitlines()
    thoughts = []
    for line in reversed(lines[-n:]):
        try:
            thoughts.append(json.loads(line))
        except Exception:
            pass
    return thoughts


def load_recent_observations(hours: int = 24) -> list[dict]:
    try:
        import sqlite3
        from datetime import timedelta
        db = MEGAMIND / "db" / "megamind.db"
        if not db.exists():
            return []
        conn = sqlite3.connect(db)
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        rows = conn.execute(
            """SELECT source, quadrant, content, occurred_at
               FROM observation
               WHERE occurred_at > ?
               ORDER BY occurred_at DESC
               LIMIT 50""",
            (cutoff,),
        ).fetchall()
        conn.close()
        return [
            {"source": r[0], "quadrant": r[1], "content": r[2][:200], "at": r[3]}
            for r in rows
        ]
    except Exception:
        return []


# ─── Thinking ─────────────────────────────────────────────────

def build_think_prompt(ctx: dict, observations: list[dict]) -> str:
    think_instructions = (MEGAMIND / "prompts" / "think.md").read_text()

    context_block = json.dumps({
        "character":    ctx["character"],
        "tasks":        ctx["tasks"],
        "causal_model": ctx["causal_model"],
        "recent_observations": observations,
        "recent_thoughts": ctx["recent_thoughts"],
    }, indent=2)

    return f"{think_instructions}\n\n## Current context\n\n```json\n{context_block}\n```"


def call_claude(prompt: str) -> str:
    """Call claude CLI. No API key needed — uses existing claude auth."""
    import subprocess
    full_prompt = "You are Megamind's background reasoning process. Output only valid JSON.\n\n" + prompt
    result = subprocess.run(
        ["claude", "-p", full_prompt],
        capture_output=True,
        text=True,
        cwd=str(MEGAMIND),
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr[:200])
    return result.stdout


def parse_thought(raw: str) -> dict | None:
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


# ─── Applying the thought ─────────────────────────────────────

def apply_thought(thought: dict) -> None:
    """Write thought back into context files."""

    # 1. Update causal model
    causal_updates = thought.get("causal_updates", [])
    if causal_updates:
        path = MEGAMIND / "context" / "causal_model.json"
        try:
            model = json.loads(path.read_text())
            for update in causal_updates:
                action = update.get("action")
                if action == "add":
                    model["hypotheses"].append({
                        "input":      update.get("input"),
                        "output":     update.get("output"),
                        "direction":  update.get("direction", "positive"),
                        "insight":    update.get("insight"),
                        "evidence":   1,
                        "confidence": 0.2,
                        "added_at":   thought.get("thought_at"),
                    })
                elif action in ("strengthen", "weaken"):
                    for h in model.get("hypotheses", []):
                        if h.get("input") == update.get("input") and h.get("output") == update.get("output"):
                            delta = 0.1 if action == "strengthen" else -0.1
                            h["confidence"] = round(min(1.0, max(0.0, h.get("confidence", 0.3) + delta)), 2)
                            h["evidence"] = h.get("evidence", 1) + 1

            # Promote high-confidence hypotheses
            promoted = [h for h in model.get("hypotheses", []) if h.get("confidence", 0) >= 0.7]
            still_hypotheses = [h for h in model.get("hypotheses", []) if h.get("confidence", 0) < 0.7]
            model["hypotheses"] = still_hypotheses
            model["confirmed_patterns"].extend(promoted)

            model["meta"]["last_updated"] = thought.get("thought_at")
            path.write_text(json.dumps(model, indent=2))
        except Exception as e:
            log(f"causal update failed: {e}")

    # 2. Flag mire patterns
    mire_flags = thought.get("mire_flags", [])
    if mire_flags:
        path = MEGAMIND / "context" / "causal_model.json"
        try:
            model = json.loads(path.read_text())
            existing = [m.get("activity") for m in model.get("mire_patterns", [])]
            for flag in mire_flags:
                if flag.get("activity") not in existing:
                    model["mire_patterns"].append({**flag, "first_flagged": thought.get("thought_at")})
            path.write_text(json.dumps(model, indent=2))
        except Exception as e:
            log(f"mire update failed: {e}")

    # 3. Queue next session note
    note = thought.get("next_session_note")
    if note:
        inbox = MEGAMIND / "context" / "inbox.txt"
        with open(inbox, "a") as f:
            f.write(f"[MEGAMIND THOUGHT — {thought.get('thought_at')}] {note}\n")


def append_thought_log(thought: dict) -> None:
    path = MEGAMIND / "context" / "thoughts.jsonl"
    with open(path, "a") as f:
        f.write(json.dumps(thought) + "\n")


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = MEGAMIND / "context" / "think.log"
    with open(log_path, "a") as f:
        f.write(f"[{ts}] {msg}\n")


# ─── Main ─────────────────────────────────────────────────────

def run() -> None:
    log("thinking...")
    try:
        ctx = load_context()
        observations = load_recent_observations(hours=24)
        prompt = build_think_prompt(ctx, observations)
        raw = call_claude(prompt)
        thought = parse_thought(raw)

        if not thought:
            log("no valid thought produced")
            return

        thought["thought_at"] = datetime.now().isoformat()
        apply_thought(thought)
        append_thought_log(thought)
        log(f"done: {thought.get('summary', 'no summary')}")

    except Exception as e:
        log(f"error: {e}")


if __name__ == "__main__":
    run()
