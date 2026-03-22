#!/usr/bin/env python3
"""
MEGAMIND — Context layer for chief of staff sessions.

This script prepares context for Claude Code sessions.
Claude Code IS the brain. This is the memory + ingest layer.

Usage:
    python main.py prep              # Pull memory, write context/brief.md
    python main.py ingest chat <file># Ingest a conversation into memory
    python main.py init              # Initialize database
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()


def cmd_prep(quiet: bool = False) -> None:
    from brain.brief import write_brief_context
    path = write_brief_context()
    if not quiet:
        console.print(f"Context ready at [bold]{path}[/bold]")
        console.print("Open Claude Code in [bold]~/megamind[/bold] — it will run the morning brief.")


def cmd_ingest(args: list[str]) -> None:
    # No args → pull from all connected MCPs
    if not args or args[0] == "mcp":
        from ingest.mcp_pull import pull
        console.print("Pulling from MCPs...")
        pull()
        return

    source = args[0]
    if source == "chat":
        if len(args) < 2:
            console.print("[red]Usage: python main.py ingest chat <file>[/red]")
            sys.exit(1)
        path = Path(args[1])
        if not path.exists():
            console.print(f"[red]File not found: {path}[/red]")
            sys.exit(1)
        from ingest.chat import ingest_file
        ingest_file(path)
    else:
        console.print(f"[red]Unknown source: {source}[/red]")
        console.print("Available: mcp, chat")
        sys.exit(1)


def cmd_init() -> None:
    from db import init_db
    init_db()
    console.print("[green]Database initialized.[/green]")


def main() -> None:
    if len(sys.argv) < 2:
        console.print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "prep":
        cmd_prep(quiet="--quiet" in sys.argv)
    elif cmd == "ingest":
        cmd_ingest(sys.argv[2:])
    elif cmd == "init":
        cmd_init()
    elif cmd == "think":
        from brain.think import run as think
        think()
    else:
        console.print(f"[red]Unknown command: {cmd}[/red]")
        console.print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
