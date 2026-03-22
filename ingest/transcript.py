"""
Claude Code transcript ingest adapter.
Reads .jsonl transcript files from ~/.claude/projects/
and extracts observations into mem0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from rich.console import Console

from db import get_conn, init_db
from brain.memory import get_memory

console = Console()

QUADRANT_KEYWORDS = {
    "spiritual":    ["scripture", "meditation", "prayer", "spiritual", "faith", "god", "worship"],
    "social":       ["call", "friend", "relationship", "adhna", "sister", "social", "people", "network"],
    "intellectual": ["license", "buffett", "reading", "learn", "study", "research", "invest", "bank"],
    "physical":     ["bjj", "blue belt", "workout", "net worth", "finance", "health", "exercise", "money"],
    "startup":      ["company", "deal", "client", "investment", "bank", "startup", "resource", "pipeline"],
}


def detect_quadrant(text: str) -> Optional[str]:
    text_lower = text.lower()
    scores = {}
    for quadrant, keywords in QUADRANT_KEYWORDS.items():
        scores[quadrant] = sum(1 for kw in keywords if kw in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


def parse_transcript(path: Path) -> list[dict]:
    """Parse Claude Code .jsonl transcript into message dicts."""
    messages = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            if obj.get("type") not in ("user", "assistant"):
                continue

            msg = obj.get("message", {})
            role = msg.get("role", obj.get("type", ""))
            content = msg.get("content", "")

            if isinstance(content, list):
                parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        parts.append(block.get("text", ""))
                content = "\n".join(parts)

            if content and isinstance(content, str) and len(content.strip()) > 20:
                messages.append({
                    "role": role,
                    "content": content.strip(),
                    "timestamp": obj.get("timestamp"),
                })

    return messages


def extract_key_exchanges(messages: list[dict]) -> list[dict]:
    """
    Extract the most signal-rich exchanges.
    Focus on: decisions, goals, mission statements, plans, personal facts.
    """
    observations = []

    # Combine into exchange pairs for context
    for i, msg in enumerate(messages):
        content = msg["content"]
        role = msg["role"]

        # Skip very short messages
        if len(content) < 30:
            continue

        # Always capture user messages — they contain intent and facts
        if role == "user":
            quadrant = detect_quadrant(content)
            observations.append({
                "source": "chat",
                "role": role,
                "content": content[:800],  # cap length
                "quadrant": quadrant,
                "timestamp": msg.get("timestamp"),
            })

        # Capture key assistant synthesis (long substantive responses)
        elif role == "assistant" and len(content) > 200:
            # Only capture sections that look like synthesis or plans
            lower = content.lower()
            is_synthesis = any(kw in lower for kw in [
                "pattern", "architecture", "the mission", "the system",
                "memory", "quadrant", "chief of staff", "synthesize",
                "the key", "what you", "morning brief"
            ])
            if is_synthesis:
                quadrant = detect_quadrant(content)
                observations.append({
                    "source": "chat",
                    "role": role,
                    "content": content[:800],
                    "quadrant": quadrant,
                    "timestamp": msg.get("timestamp"),
                })

    return observations


def ingest_transcript(path: Path) -> int:
    init_db()
    console.print(f"[dim]Parsing {path.name}...[/dim]")

    messages = parse_transcript(path)
    console.print(f"[dim]{len(messages)} messages found[/dim]")

    observations = extract_key_exchanges(messages)
    console.print(f"[dim]{len(observations)} signal observations extracted[/dim]")

    mem = get_memory()
    conn = get_conn()
    stored = 0

    for obs in observations:
        content = obs["content"]
        quadrant = obs["quadrant"]
        role = obs["role"]
        ts = obs.get("timestamp")

        conn.execute(
            "INSERT INTO observation (source, quadrant, content, occurred_at, processed) VALUES (?, ?, ?, ?, 0)",
            ("chat", quadrant, content, ts or datetime.now().isoformat()),
        )

        tag = f"[{quadrant}] " if quadrant else ""
        mem.add(
            f"{tag}[{role}] {content}",
            metadata={"source": "claude_transcript", "quadrant": quadrant,
                      "role": role, "file": path.name},
        )
        stored += 1

    conn.commit()
    conn.close()
    console.print(f"[green]✓ {stored} observations stored from {path.name}[/green]")
    return stored


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default: ingest most recent transcript
        transcripts = sorted(
            Path.home().glob(".claude/projects/-Users-reify/*.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not transcripts:
            console.print("[red]No transcripts found[/red]")
            sys.exit(1)
        path = transcripts[0]
        console.print(f"[dim]Most recent: {path.name}[/dim]")
    else:
        path = Path(sys.argv[1])

    ingest_transcript(path)
