"""
Megamind memory — flat markdown file.
Claude reads and writes context/memory.md directly.
This module provides helpers for appending observations programmatically.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

MEGAMIND = Path(__file__).parent.parent
MEMORY_FILE = MEGAMIND / "context" / "memory.md"


def append(content: str, section: str = "observations") -> None:
    """Append an observation to memory.md."""
    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text("# Memory\n\n")

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- [{ts}] {content}\n"

    text = MEMORY_FILE.read_text()
    header = f"## {section.title()}"
    if header in text:
        text = text.replace(header, f"{header}\n{entry}", 1)
    else:
        text += f"\n{header}\n{entry}"

    MEMORY_FILE.write_text(text)


def read() -> str:
    """Return full memory contents for Claude to read."""
    if not MEMORY_FILE.exists():
        return ""
    return MEMORY_FILE.read_text()
