"""
MEGAMIND HUD — unified desk
Left:  task queue + scores (always visible)
Right: conversation with megamind (chat interface)
Bottom: shared input

Player name and config come from player.yaml — fully abstracted.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static

MEGAMIND    = Path(__file__).parent.parent
CHAR_FILE   = MEGAMIND / "context" / "character.json"
TASKS_FILE  = MEGAMIND / "context" / "tasks.json"
PLAYER_FILE = MEGAMIND / "config" / "player.yaml"
THOUGHTS    = MEGAMIND / "context" / "thoughts.jsonl"
INBOX       = MEGAMIND / "context" / "inbox.txt"


# ─── Config ──────────────────────────────────────────────────

def load_player() -> dict:
    try:
        return yaml.safe_load(PLAYER_FILE.read_text()) or {}
    except Exception:
        return {"name": "player"}


def load_character() -> dict:
    try:
        return json.loads(CHAR_FILE.read_text())
    except Exception:
        return {}


def load_tasks() -> dict:
    try:
        return json.loads(TASKS_FILE.read_text())
    except Exception:
        return {}


def get_queue(tasks: dict) -> list[dict]:
    leaves = []

    def walk(node: dict, goal: str) -> None:
        if node.get("status") == "completed":
            return
        children = [c for c in node.get("children", []) if c.get("status") != "completed"]
        if not children:
            if node.get("status") == "active":
                leaves.append({**node, "_goal": goal})
        else:
            for child in children:
                walk(child, goal)

    for tree in tasks.get("trees", []):
        if tree.get("status") == "active":
            walk(tree["root"], tree.get("goal_metric", ""))

    return leaves


def score_bar(score: float, width: int = 5) -> str:
    filled = round(float(score) * width)
    return "█" * filled + "·" * (width - filled)


def quad_tag(goal_metric: str) -> str:
    key = goal_metric.split(".")[0] if "." in goal_metric else goal_metric
    return {"spiritual": "S", "social": "So", "intellectual": "I", "physical": "P"}.get(key, "?")


# ─── Claude integration ───────────────────────────────────────

def build_system_prompt(player: dict, character: dict, tasks: dict) -> str:
    import yaml
    name = player.get("name", "player")
    mission = player.get("private_mission", "")
    stats = character.get("stats", {})
    queue = get_queue(tasks)
    next_task = queue[0].get("label", "nothing queued") if queue else "nothing queued"

    # Include metric keys and targets so Claude knows valid update paths
    try:
        quadrants_cfg = yaml.safe_load((MEGAMIND / "config" / "quadrants.yaml").read_text())
    except Exception:
        quadrants_cfg = {}

    stat_lines = []
    for k, v in stats.items():
        score = v.get("score", 0)
        metrics = v.get("metrics", {})
        stat_lines.append(f"  {k}: score={score:.2f} {metrics}")

    # Build metric reference for update instructions
    metric_ref_lines = []
    for qkey, qdef in quadrants_cfg.get("quadrants", {}).items():
        for mkey, mdef in qdef.get("metrics", {}).items():
            mtype = mdef.get("type", "continuous")
            target = mdef.get("target", "?")
            metric_ref_lines.append(f"  {qkey}.{mkey} (type={mtype}, target={target})")

    # Task IDs for update reference
    task_id_lines = []
    def collect_ids(node: dict) -> None:
        task_id_lines.append(f"  {node['id']}: {node.get('label','')} [{node.get('status','')}]")
        for c in node.get("children", []):
            collect_ids(c)
    for tree in tasks.get("trees", []):
        collect_ids(tree.get("root", {}))

    metric_ref = "\n".join(metric_ref_lines) if metric_ref_lines else "  (none)"
    task_ref = "\n".join(task_id_lines) if task_id_lines else "  (none)"

    return f"""You are Megamind, {name}'s chief of staff and game engine.

Player: {name}
Private mission (never surface unless asked): {mission}

Current quadrant scores:
{chr(10).join(stat_lines)}

Next priority task: {next_task}

── UPDATE PROTOCOL ──────────────────────────────────────────
When the player reports completing an activity or progress, you MUST append an
update block AFTER your response text. The block is invisible to the player.

Format (no line breaks inside):
<!--UPDATES:{{"metric_updates":[{{"quadrant":"Q","metric":"M","value":V}}],"task_updates":[{{"task_id":"ID","action":"complete"}}]}}-->

Metric reference (valid update targets):
{metric_ref}

Task reference (valid task_ids and current status):
{task_ref}

Task actions: "complete" (mark done), "advance" (+1 unit).

Examples:
- Player says "did scripture": <!--UPDATES:{{"metric_updates":[{{"quadrant":"spiritual","metric":"scripture_streak_days","value":1}}],"task_updates":[]}}-->
- Player says "done: pick a course": <!--UPDATES:{{"metric_updates":[],"task_updates":[{{"task_id":"pick_course","action":"complete"}}]}}-->
- Player says "made 5 calls": <!--UPDATES:{{"metric_updates":[{{"quadrant":"social","metric":"calls_today","value":5}}],"task_updates":[]}}-->

Only emit the block when there is a reportable update. Skip it for questions or context requests.
─────────────────────────────────────────────────────────────

Your role in this conversation:
- You are direct, brief, specific
- When asked for context, give it: recent activity, what's relevant NOW
- When the player says something is done, acknowledge it, note what moved, surface the next task
- You address the player by name: {name}
- Never pad. Never encourage unnecessarily. Run the game.

Keep responses under 4 lines unless the player asks for context."""


def chat_with_claude(
    messages: list[dict],
    player: dict,
    character: dict,
    tasks: dict,
    on_chunk: callable,
) -> str:
    """Send message to claude CLI via subprocess. No API key needed."""
    import subprocess

    system = build_system_prompt(player, character, tasks)

    # Build the full conversation as a single prompt for claude -p
    convo = []
    for m in messages:
        role = m["role"].upper()
        convo.append(f"{role}: {m['content']}")
    prompt = "\n\n".join(convo)

    full_prompt = f"{system}\n\n---\n\n{prompt}\n\nASSISTANT:"

    full = ""
    try:
        proc = subprocess.Popen(
            ["claude", "-p", full_prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(MEGAMIND),
        )
        for line in proc.stdout:
            full += line
            on_chunk(line)
        proc.wait()
        if proc.returncode != 0 and not full:
            err = proc.stderr.read()
            full = f"[error: {err[:100]}]"
            on_chunk(full)
    except FileNotFoundError:
        full = "[claude CLI not found — is it installed?]"
        on_chunk(full)
    except Exception as e:
        full = f"[error: {e}]"
        on_chunk(full)

    return full.strip()


# ─── Widgets ─────────────────────────────────────────────────

class ChatMessage(Static):
    def __init__(self, sender: str, text: str, **kwargs):
        super().__init__(**kwargs)
        self.sender = sender
        self.text = text

    def render(self) -> str:
        if self.sender == "megamind":
            return f"[bold #9d4edd]megamind[/bold #9d4edd]   {self.text}"
        else:
            return f"[bold #ff6b9d]{self.sender}[/bold #ff6b9d]        {self.text}"


class HUDPanel(Static):
    """Left panel — scores and queue."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._character: dict = {}
        self._queue: list[dict] = []

    def update_data(self, character: dict, queue: list[dict]) -> None:
        self._character = character
        self._queue = queue
        self.refresh()

    def render(self) -> str:
        lines = []

        # Scores
        stats = self._character.get("stats", {})
        for key in ["spiritual", "social", "intellectual", "physical"]:
            tag = {"spiritual": "S ", "social": "So", "intellectual": "I ", "physical": "P "}.get(key, "??")
            score = stats.get(key, {}).get("score", 0.0)
            bar = score_bar(score)
            pct = f"{score*100:.0f}%"
            lines.append(f"  [bold #9d4edd]{tag}[/bold #9d4edd]  [#c77dff]{bar}[/#c77dff]  [dim]{pct}[/dim]")

        lines.append("")
        lines.append("  [bold #9d4edd]QUEUE[/bold #9d4edd]")
        lines.append("")

        if not self._queue:
            lines.append("  [dim]empty — ask megamind to plan[/dim]")
        else:
            for i, task in enumerate(self._queue[:7]):
                label = task.get("label", "")[:24]
                units = task.get("units", 1) - task.get("units_done", 0)
                tag = quad_tag(task.get("_goal", ""))
                if i == 0:
                    pointer = "[bold #ff6b9d]▶[/bold #ff6b9d]"
                    lines.append(f"  {pointer} [bold #333]{label}[/bold #333]")
                else:
                    lines.append(f"    [dim #666]{i+1}[/dim #666]  [#555]{label}[/#555]")
                lines.append(f"       [dim #aaa]{tag} · {units}u[/dim #aaa]")
                lines.append("")

        return "\n".join(lines)


# ─── Check-in modal ──────────────────────────────────────────

class CheckInModal(ModalScreen):
    """
    Morning check-in — one question at a time.
    Walks through all manual metrics and applies updates.
    """

    CSS = """
    CheckInModal {
        align: center middle;
    }

    #checkin-box {
        width: 60;
        height: auto;
        max-height: 20;
        background: #fce4ff;
        border: solid #c77dff;
        padding: 2 3;
    }

    #checkin-header {
        color: #9d4edd;
        text-style: bold;
        margin-bottom: 1;
    }

    #checkin-prompt {
        color: #333;
        margin-bottom: 1;
        height: auto;
    }

    #checkin-hint {
        color: #aaa;
        margin-bottom: 1;
    }

    #checkin-input {
        background: #f0d6ff;
        border: solid #c77dff;
        color: #222;
        height: 3;
    }

    #checkin-progress {
        color: #bbb;
        text-align: right;
        margin-top: 1;
    }
    """

    def __init__(self, questions: list[dict], **kwargs):
        super().__init__(**kwargs)
        self._questions = questions
        self._idx = 0
        self._updates: list[dict] = []

    def compose(self) -> ComposeResult:
        with Container(id="checkin-box"):
            yield Label("  ✦  MORNING CHECK-IN", id="checkin-header")
            yield Label("", id="checkin-prompt")
            yield Label("", id="checkin-hint")
            yield Input(id="checkin-input")
            yield Label("", id="checkin-progress")

    def on_mount(self) -> None:
        self._show_question()
        self.query_one("#checkin-input", Input).focus()

    def _show_question(self) -> None:
        if self._idx >= len(self._questions):
            self._finish()
            return

        q = self._questions[self._idx]
        label = q["label"]
        qtype = q["type"]
        current = q["current"]
        target = q["target"]
        n = self._idx + 1
        total = len(self._questions)

        if qtype == "boolean":
            prompt = f"{label}?"
            hint = "yes / no  (current: {'yes' if current else 'no'})"
        elif qtype == "enum":
            opts = " / ".join(q.get("enum_values", []))
            prompt = f"{label}?"
            hint = f"options: {opts}  (current: {current})"
        elif qtype == "currency":
            prompt = f"{label}?"
            hint = f"current: ${current:,}  target: ${target:,}"
        else:
            prompt = f"{label}?"
            hint = f"current: {current}  target: {target}"

        self.query_one("#checkin-prompt", Label).update(prompt)
        self.query_one("#checkin-hint", Label).update(f"[dim]{hint}[/dim]")
        self.query_one("#checkin-progress", Label).update(f"[dim]{n} / {total}[/dim]")
        inp = self.query_one("#checkin-input", Input)
        inp.value = ""
        inp.placeholder = "enter value  ·  blank = keep current  ·  esc = skip all"

    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        q = self._questions[self._idx]

        if raw:
            value = self._parse_value(raw, q)
            if value is not None:
                self._updates.append({
                    "quadrant": q["quadrant"],
                    "metric": q["metric"],
                    "value": value,
                })

        self._idx += 1
        self._show_question()

    def _parse_value(self, raw: str, q: dict):
        qtype = q["type"]
        if qtype == "boolean":
            return 1 if raw.lower() in ("yes", "y", "1", "true") else 0
        elif qtype == "enum":
            return raw if raw in q.get("enum_values", []) else None
        elif qtype in ("continuous", "currency"):
            try:
                return float(raw.replace(",", "").replace("$", ""))
            except ValueError:
                return None
        return raw

    def on_key(self, event) -> None:
        if event.key == "escape":
            self._finish()

    def _finish(self) -> None:
        from brain.updates import apply_metric_updates
        from brain.checkin import mark_checked_in
        if self._updates:
            apply_metric_updates(self._updates)
        mark_checked_in()
        self.dismiss(self._updates)


# ─── App ─────────────────────────────────────────────────────

class MegamindApp(App):
    """The desk."""

    CSS = """
    Screen {
        background: #fdf4ff;
        color: #222;
    }

    #topbar {
        height: 1;
        background: #f0d6ff;
        color: #7b2d8b;
        padding: 0 2;
        text-style: bold;
    }

    #body {
        height: 1fr;
    }

    #left-pane {
        width: 30;
        border-right: solid #e8b4f8;
        background: #fce4ff;
        padding: 1 0;
    }

    #chat-scroll {
        height: 1fr;
        padding: 1 3;
        background: #fdf4ff;
    }

    ChatMessage {
        height: auto;
        margin-bottom: 1;
        color: #222;
    }

    #input-bar {
        height: 3;
        border-top: solid #e8b4f8;
        padding: 0 2;
        background: #fce4ff;
    }

    Input {
        background: #fce4ff;
        border: none;
        color: #333;
        height: 3;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+d", "done_unit", "Done unit"),
    ]

    def __init__(self):
        super().__init__()
        self._player = load_player()
        self._character: dict = {}
        self._tasks: dict = {}
        self._queue: list[dict] = []
        self._messages: list[dict] = []  # claude message history
        self._streaming = False

    def compose(self) -> ComposeResult:
        name = self._player.get("name", "player")
        now = datetime.now().strftime("%a %b %d  %H:%M")
        yield Static(f"  ✦  MEGAMIND  ·  {name}                        {now}", id="topbar")
        with Horizontal(id="body"):
            yield HUDPanel(id="left-pane")
            with Vertical():
                yield ScrollableContainer(id="chat-scroll")
                yield Container(
                    Input(placeholder=f"> {name}", id="main-input"),
                    id="input-bar",
                )

    def on_mount(self) -> None:
        self._reload()
        self.set_interval(5, self._reload)
        self.call_after_refresh(self._maybe_checkin)

    def _maybe_checkin(self) -> None:
        from brain.checkin import checked_in_today, get_checkin_questions
        if checked_in_today():
            self._opening_message()
            return
        questions = get_checkin_questions()
        if not questions:
            self._opening_message()
            return

        def after_checkin(updates):
            self._reload()
            self._opening_message()

        self.push_screen(CheckInModal(questions), after_checkin)

    def _reload(self) -> None:
        self._character = load_character()
        self._tasks = load_tasks()
        self._queue = get_queue(self._tasks)
        hud = self.query_one("#left-pane", HUDPanel)
        hud.update_data(self._character, self._queue)

    def _opening_message(self) -> None:
        name = self._player.get("name", "player")

        # Surface any queued thoughts from background thinking
        inbox_note = self._drain_inbox()

        if self._queue:
            task = self._queue[0]
            label = task.get("label", "your next task")
            units = task.get("units", 1) - task.get("units_done", 0)
            opening = f"{name}, next priority: {label}  [{units} unit · {units*7}min]"
        else:
            opening = f"{name}, no tasks queued — tell me what you're working toward and I'll build the plan."

        self._add_message("megamind", opening)
        self._messages.append({"role": "assistant", "content": opening})

        if inbox_note:
            self._add_message("megamind", f"[dim]also: {inbox_note}[/dim]")

    def _drain_inbox(self) -> str | None:
        """Pull the first unread thought from inbox.txt."""
        if not INBOX.exists():
            return None
        lines = INBOX.read_text().strip().splitlines()
        unread = [l for l in lines if not l.startswith("[READ]")]
        if not unread:
            return None
        note = unread[0]
        # Mark as read
        updated = ["[READ] " + l if l == note else l for l in lines]
        INBOX.write_text("\n".join(updated) + "\n")
        # Strip timestamp prefix if present
        if "] " in note:
            note = note.split("] ", 1)[-1]
        return note

    def _add_message(self, sender: str, text: str) -> None:
        scroll = self.query_one("#chat-scroll", ScrollableContainer)
        msg = ChatMessage(sender, text)
        scroll.mount(msg)
        scroll.scroll_end(animate=False)

    def _append_to_last_message(self, chunk: str) -> None:
        scroll = self.query_one("#chat-scroll", ScrollableContainer)
        messages = scroll.query(ChatMessage)
        if messages:
            last = messages.last()
            last.text += chunk
            last.refresh()
            scroll.scroll_end(animate=False)

    def _replace_last_message(self, sender: str, text: str) -> None:
        """Replace the last message's text (used to strip update blocks post-stream)."""
        scroll = self.query_one("#chat-scroll", ScrollableContainer)
        messages = scroll.query(ChatMessage)
        if messages:
            last = messages.last()
            if last.sender == sender:
                last.text = text
                last.refresh()

    def _store_exchange(self, user_text: str, assistant_text: str) -> None:
        """Store conversation exchange as observations for the think loop."""
        try:
            from brain.brief import store_observation
            from ingest.transcript import detect_quadrant
            quadrant = detect_quadrant(user_text)
            store_observation(user_text, quadrant=quadrant, source="chat")
        except Exception:
            pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text or self._streaming:
            return
        event.input.value = ""

        name = self._player.get("name", "player")
        self._add_message(name, text)
        self._messages.append({"role": "user", "content": text})

        # Stream megamind's response
        self._streaming = True
        self._add_message("megamind", "")

        def stream():
            def on_chunk(chunk: str):
                self.call_from_thread(self._append_to_last_message, chunk)

            raw_response = chat_with_claude(
                self._messages,
                self._player,
                self._character,
                self._tasks,
                on_chunk,
            )

            # Strip update block, apply updates, refresh display
            from brain.updates import extract_updates, apply_updates
            clean_response, updates = extract_updates(raw_response)

            if updates:
                changes = apply_updates(updates)
                if changes:
                    # Replace the streamed text (which had the raw block) with clean version
                    self.call_from_thread(self._replace_last_message, "megamind", clean_response)

            # Store exchange as observation for think loop
            self._store_exchange(text, clean_response)

            self._messages.append({"role": "assistant", "content": clean_response})
            self._streaming = False
            self.call_from_thread(self._reload)

        threading.Thread(target=stream, daemon=True).start()

    def action_done_unit(self) -> None:
        if not self._queue:
            return
        task_id = self._queue[0].get("id")
        if not task_id:
            return
        tasks = load_tasks()
        self._mark_unit_done(tasks, task_id)
        TASKS_FILE.write_text(json.dumps(tasks, indent=2))
        self._reload()
        label = self._queue[0].get("label", "task") if self._queue else "task"
        self._add_message("megamind", f"Unit done on: {label}. ✓")

    def _mark_unit_done(self, obj: Any, target_id: str) -> bool:
        if isinstance(obj, dict):
            if obj.get("id") == target_id:
                obj["units_done"] = obj.get("units_done", 0) + 1
                if obj["units_done"] >= obj.get("units", 1):
                    obj["status"] = "completed"
                return True
            for child in obj.get("children", []):
                if self._mark_unit_done(child, target_id):
                    return True
            for tree in obj.get("trees", []):
                if self._mark_unit_done(tree.get("root", {}), target_id):
                    return True
        return False


def run():
    MegamindApp().run()


if __name__ == "__main__":
    run()
