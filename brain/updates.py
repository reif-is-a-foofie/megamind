"""
Parse and apply structured update blocks from megamind's chat responses.

Claude is instructed to emit an update block at the end of responses when
the player reports progress. Format:

  <!--UPDATES:{"metric_updates":[...],"task_updates":[...]}-->

This module strips the block from the display text, parses it, and applies it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

MEGAMIND = Path(__file__).parent.parent
TASKS_FILE = MEGAMIND / "context" / "tasks.json"

UPDATE_PATTERN = re.compile(r'<!--UPDATES:(.*?)-->', re.DOTALL)


# ─── Extraction ───────────────────────────────────────────────

def extract_updates(response: str) -> tuple[str, dict]:
    """
    Find and remove the UPDATES block from a Claude response.
    Returns (clean_text, updates_dict).
    """
    match = UPDATE_PATTERN.search(response)
    if not match:
        return response, {}

    raw = match.group(1).strip()
    clean = UPDATE_PATTERN.sub("", response).strip()

    try:
        updates = json.loads(raw)
    except json.JSONDecodeError:
        return clean, {}

    return clean, updates


# ─── Application ──────────────────────────────────────────────

def apply_metric_updates(metric_updates: list[dict]) -> list[str]:
    """
    Apply a list of metric update dicts to character.json.
    Each dict: {"quadrant": str, "metric": str, "value": any}
    Returns list of human-readable change descriptions.
    """
    from brain.score import update_metric
    applied = []
    for upd in metric_updates:
        q = upd.get("quadrant")
        m = upd.get("metric")
        v = upd.get("value")
        if q and m and v is not None:
            try:
                char = update_metric(q, m, v)
                score = char.get("stats", {}).get(q, {}).get("score", 0)
                applied.append(f"{q}.{m} → {v}  (score {score:.2f})")
            except Exception as e:
                applied.append(f"failed {q}.{m}: {e}")
    return applied


def apply_task_updates(task_updates: list[dict]) -> list[str]:
    """
    Apply task status changes to tasks.json.
    Each dict: {"task_id": str, "action": "complete"|"advance"|"add", ...}
    Returns list of human-readable change descriptions.
    """
    if not TASKS_FILE.exists():
        return []

    tasks = json.loads(TASKS_FILE.read_text())
    applied = []

    for upd in task_updates:
        action = upd.get("action")
        task_id = upd.get("task_id")

        if action == "complete" and task_id:
            if _mark_complete(tasks, task_id):
                applied.append(f"task '{task_id}' completed")
            else:
                applied.append(f"task '{task_id}' not found")

        elif action == "advance" and task_id:
            if _increment_units(tasks, task_id):
                applied.append(f"task '{task_id}' +1 unit")
            else:
                applied.append(f"task '{task_id}' not found")

    TASKS_FILE.write_text(json.dumps(tasks, indent=2))
    return applied


def _find_node(obj: Any, target_id: str) -> dict | None:
    if isinstance(obj, dict):
        if obj.get("id") == target_id:
            return obj
        for child in obj.get("children", []):
            found = _find_node(child, target_id)
            if found:
                return found
        for tree in obj.get("trees", []):
            found = _find_node(tree.get("root", {}), target_id)
            if found:
                return found
    return None


def _mark_complete(tasks: dict, task_id: str) -> bool:
    node = _find_node(tasks, task_id)
    if node:
        node["status"] = "completed"
        node["units_done"] = node.get("units", 1)
        _unlock_next(tasks, task_id)
        return True
    return False


def _increment_units(tasks: dict, task_id: str) -> bool:
    node = _find_node(tasks, task_id)
    if node:
        node["units_done"] = node.get("units_done", 0) + 1
        if node["units_done"] >= node.get("units", 1):
            node["status"] = "completed"
            _unlock_next(tasks, task_id)
        return True
    return False


def _unlock_next(tasks: dict, completed_id: str) -> None:
    """When a node completes, unblock siblings that were blocked by it."""
    def walk(node: dict) -> None:
        for child in node.get("children", []):
            blocked_by = child.get("blocked_by", [])
            if completed_id in blocked_by:
                blocked_by.remove(completed_id)
                if not blocked_by and child.get("status") == "blocked":
                    child["status"] = "active"
            walk(child)

    for tree in tasks.get("trees", []):
        walk(tree.get("root", {}))


# ─── Queue ────────────────────────────────────────────────────

def queue_task(
    task_id: str,
    label: str,
    acceptance: str,
    *,
    tree_id: str | None = None,
    goal_metric: str | None = None,
    note: str = "",
    units: int = 1,
) -> bool:
    """
    Add a task to tasks.json if it doesn't already exist.
    Returns True if added, False if already present.
    Any subsystem can call this to surface required work.
    """
    if not TASKS_FILE.exists():
        return False

    tasks = json.loads(TASKS_FILE.read_text())

    if _find_node(tasks, task_id):
        return False  # already queued

    node: dict[str, Any] = {
        "id": task_id,
        "label": label,
        "status": "active",
        "acceptance": acceptance,
        "units": units,
        "units_done": 0,
        "blocked_by": [],
        "children": [],
    }
    if note:
        node["note"] = note

    tasks.setdefault("trees", []).append({
        "id": tree_id or task_id,
        "goal_metric": goal_metric or task_id,
        "goal_value": "done",
        "status": "active",
        "root": node,
    })

    TASKS_FILE.write_text(json.dumps(tasks, indent=2))
    return True


# ─── Combined apply ───────────────────────────────────────────

def apply_updates(updates: dict) -> list[str]:
    """Apply all updates from a parsed update block. Returns change log."""
    changes = []
    changes += apply_metric_updates(updates.get("metric_updates", []))
    changes += apply_task_updates(updates.get("task_updates", []))
    return changes
