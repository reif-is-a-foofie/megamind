"""
Chat ingest adapter.
Takes Claude conversation exports (JSON or plain text),
extracts observations, tags by quadrant, stores in DB + mem0.

This is the first and richest data source — every conversation
is signal about what you're thinking about, working on, and stuck on.

Usage:
    python -m ingest.chat path/to/conversation.json
    python -m ingest.chat path/to/conversation.txt
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import anthropic
from rich.console import Console

from db import get_conn, init_db
from brain.memory import get_memory

console = Console()

QUADRANTS = ["spiritual", "social", "intellectual", "physical", "startup", "meta"]

TAGGER_PROMPT = """
You are analyzing a conversation to extract observations for a personal life OS.

For each meaningful exchange in the conversation, identify:
1. What quadrant it relates to: spiritual | social | intellectual | physical | startup | meta
2. A concise summary of the observation (1-2 sentences)
3. Importance: 0.0-1.0
4. Any people mentioned by name
5. Any decisions made

Return a JSON array of observations:
[
  {
    "quadrant": "intellectual",
    "content": "Researching MCP protocol for building AI tool integrations",
    "importance": 0.7,
    "people": [],
    "decision": null
  }
]

Only include observations that have lasting signal — skip pleasantries, filler, and
anything that will be irrelevant in 48 hours.
"""


def extract_observations(text: str) -> list[dict]:
    """Use Claude to extract structured observations from conversation text."""
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=TAGGER_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Extract observations from this conversation:\n\n{text[:12000]}"
        }],
    )

    raw = response.content[0].text
    # Extract JSON from response
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if not match:
        return []

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        console.print("[red]Failed to parse observations JSON[/red]")
        return []


def load_conversation(path: Path) -> str:
    """Load conversation from JSON export or plain text."""
    text = path.read_text()

    if path.suffix == ".json":
        try:
            data = json.loads(text)
            # Handle Claude conversation export format
            if isinstance(data, list):
                parts = []
                for msg in data:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    if isinstance(content, list):
                        content = " ".join(
                            c.get("text", "") for c in content
                            if isinstance(c, dict) and c.get("type") == "text"
                        )
                    parts.append(f"{role.upper()}: {content}")
                return "\n\n".join(parts)
            elif isinstance(data, dict):
                # Single conversation object
                messages = data.get("messages", [])
                parts = []
                for msg in messages:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    parts.append(f"{role.upper()}: {content}")
                return "\n\n".join(parts)
        except json.JSONDecodeError:
            pass

    return text


def ingest_file(
    path: Path,
    user_id: str = "reify",
    occurred_at: Optional[datetime] = None,
) -> int:
    """
    Ingest a conversation file.
    Returns number of observations stored.
    """
    init_db()

    console.print(f"[dim]Loading {path.name}...[/dim]")
    text = load_conversation(path)

    console.print("[dim]Extracting observations...[/dim]")
    observations = extract_observations(text)

    if not observations:
        console.print("[yellow]No observations extracted.[/yellow]")
        return 0

    conn = get_conn()
    mem = get_memory()
    stored = 0

    for obs in observations:
        content = obs.get("content", "").strip()
        if not content:
            continue

        quadrant = obs.get("quadrant")
        importance = float(obs.get("importance", 0.5))
        meta = {
            "people": obs.get("people", []),
            "decision": obs.get("decision"),
            "source_file": path.name,
        }

        conn.execute(
            """
            INSERT INTO observation (source, quadrant, content, meta, importance, occurred_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "chat",
                quadrant,
                content,
                json.dumps(meta),
                importance,
                (occurred_at or datetime.now()).isoformat(),
            ),
        )

        mem_text = f"[{quadrant or 'general'}] {content}"
        mem.add(mem_text, metadata={"source": "chat", "quadrant": quadrant,
                                     "importance": importance, "file": path.name})
        stored += 1

    conn.commit()
    conn.close()

    console.print(f"[green]Stored {stored} observations from {path.name}[/green]")
    return stored


if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("Usage: python -m ingest.chat <path/to/conversation>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        console.print(f"[red]File not found: {path}[/red]")
        sys.exit(1)

    ingest_file(path)
