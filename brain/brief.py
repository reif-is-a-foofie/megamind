"""
Morning brief context loader.
Queries memory, formats current state, writes context/brief.md.
Claude reads this file at session start and runs the brief.

No direct API calls. Claude Code IS the brain.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from rich.console import Console

from db import get_conn, init_db
from brain.memory import get_memory

console = Console()
CONTEXT_PATH = Path(__file__).parent.parent / "context" / "brief.md"
CONTEXT_PATH.parent.mkdir(exist_ok=True)


def pull_memory() -> dict[str, list[str]]:
    mem = get_memory()
    queries = {
        "quadrant_state": "current quadrant state and progress toward goals",
        "in_flight":      "in-flight work and open threads",
        "people":         "people I need to contact or follow up with",
        "patterns":       "behavioral patterns and recurring tendencies",
        "startup":        "startup pipeline, deals, and contacts",
        "decisions":      "recent decisions and commitments",
    }
    result: dict[str, list[str]] = {}
    for key, q in queries.items():
        hits = mem.search(q, limit=5)
        result[key] = [r.get("memory", "") for r in hits if r.get("memory")]
    return result


def write_brief_context() -> Path:
    init_db()
    console.print("[dim]Querying memory...[/dim]")
    memory = pull_memory()
    now = datetime.now().strftime("%A %B %d, %Y — %I:%M %p")

    lines = ["# MEGAMIND CONTEXT", f"_Prepared: {now}_", ""]
    section_labels = {
        "quadrant_state": "Quadrant State",
        "in_flight":      "In Flight",
        "people":         "People",
        "patterns":       "Patterns",
        "startup":        "Startup",
        "decisions":      "Recent Decisions",
    }
    has_memory = False
    for key, label in section_labels.items():
        items = memory.get(key, [])
        if items:
            has_memory = True
            lines.append(f"## {label}")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")

    if not has_memory:
        lines.append("_No memory yet. This may be the first session._")
        lines.append("")

    # Append live MCP data if available
    mcp_data_path = Path(__file__).parent.parent / "context" / "mcp_data.json"
    if mcp_data_path.exists():
        import json
        try:
            mcp = json.loads(mcp_data_path.read_text())
            pulled_at = mcp.get("pulled_at", "")
            lines.append(f"## Live Data  _(pulled {pulled_at[:16]})_")

            if cal := mcp.get("apple", {}).get("calendar_today"):
                lines.append("### Calendar today")
                lines.append(str(cal))
                lines.append("")

            if msgs := mcp.get("apple", {}).get("recent_messages"):
                lines.append("### Recent messages")
                lines.append(str(msgs)[:800])
                lines.append("")

            if gmail := mcp.get("gmail", {}).get("gmail_unread"):
                lines.append("### Gmail unread")
                lines.append(str(gmail)[:800])
                lines.append("")
        except Exception:
            pass

    CONTEXT_PATH.write_text("\n".join(lines))
    console.print(f"[green]Context written → {CONTEXT_PATH}[/green]")
    return CONTEXT_PATH


def store_observation(content: str, quadrant: str | None, source: str = "chat") -> None:
    init_db()
    mem = get_memory()
    conn = get_conn()
    conn.execute(
        "INSERT INTO observation (source, quadrant, content, occurred_at) VALUES (?, ?, ?, ?)",
        (source, quadrant, content, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    tag = f"[{quadrant}] " if quadrant else ""
    mem.add(f"{tag}{content}", metadata={"source": source, "quadrant": quadrant})
