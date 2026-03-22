"""
MCP sync — reads quadrants.yaml tracked_by fields, maps to packages,
adds any missing servers to .mcp.json.

Run: python3 brain/mcp_sync.py
Also called by install.sh and the daily ingest cron.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

MEGAMIND = Path(__file__).parent.parent
MCP_JSON = MEGAMIND / ".mcp.json"
QUADRANTS = MEGAMIND / "config" / "quadrants.yaml"

# ── Registry: tracked_by key → MCP server config ──────────────────────────
# Add entries here as new MCPs become available.
# "needs_auth" = True means user must run an auth step manually.
REGISTRY: dict[str, dict] = {
    # ── Native macOS (apple-mcp) ──────────────────────────────────
    # Covers: Messages, Calendar, Contacts, Mail, Maps, Notes, Reminders, Health
    "apple": {
        "type": "stdio",
        "command": "/Users/reify/.bun/bin/bunx",
        "args": ["--no-cache", "apple-mcp@latest"],
    },
    "calendar_mcp": {"ref": "apple"},
    "phone_mcp":    {"ref": "apple"},
    "health_mcp":   {"ref": "apple"},

    # ── Gmail ─────────────────────────────────────────────────────
    "gmail": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@gongrzhe/server-gmail-autoauth-mcp"],
        "needs_auth": "npx -y @gongrzhe/server-gmail-autoauth-mcp auth",
    },

    # ── Reading (Readwise) ────────────────────────────────────────
    "readwise_mcp": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@readwise/mcp"],
        "env_required": ["READWISE_TOKEN"],
        "note": "Set READWISE_TOKEN in ~/.megamind.env — get it at readwise.io/access_token",
    },

    # ── Financial (Plaid) ─────────────────────────────────────────
    "financial_mcp": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-plaid"],
        "env_required": ["PLAID_CLIENT_ID", "PLAID_SECRET"],
        "note": "Plaid sandbox keys at dashboard.plaid.com — set in ~/.megamind.env",
    },

    # ── GitHub — code activity, project velocity ──────────────────
    "github_mcp": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env_required": ["GITHUB_TOKEN"],
        "note": "Create token at github.com/settings/tokens (repo scope) — set GITHUB_TOKEN in ~/.megamind.env",
    },

    # ── Notion — notes, documents, thinking ──────────────────────
    "notion_mcp": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-notion"],
        "env_required": ["NOTION_API_KEY"],
        "note": "Create integration at notion.so/my-integrations — set NOTION_API_KEY in ~/.megamind.env",
    },

    # ── LinkedIn — professional network (unofficial) ──────────────
    "linkedin_mcp": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "mcp-linkedin"],
        "env_required": ["LINKEDIN_EMAIL", "LINKEDIN_PASSWORD"],
        "note": "Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in ~/.megamind.env",
    },
}


def _tracked_by_values() -> set[str]:
    cfg = yaml.safe_load(QUADRANTS.read_text())
    values = set()
    for qdef in cfg.get("quadrants", {}).values():
        for mdef in qdef.get("metrics", {}).values():
            tb = mdef.get("tracked_by", "manual")
            if tb and tb != "manual":
                # strip inline comments
                tb = tb.split("#")[0].strip()
                values.add(tb)
    return values


def _load_mcp() -> dict:
    if MCP_JSON.exists():
        return json.loads(MCP_JSON.read_text())
    return {}


def _save_mcp(cfg: dict) -> None:
    MCP_JSON.write_text(json.dumps(cfg, indent=2) + "\n")


# MCPs megamind proactively wants — not tied to a specific metric,
# but valuable for understanding the player's world.
PROACTIVE: list[str] = [
    "github_mcp",   # code activity, project velocity
    "notion_mcp",   # notes, documents, thinking
    "linkedin_mcp", # professional network
]


def sync() -> list[str]:
    """
    Ensure every tracked_by MCP is wired in .mcp.json.
    Also installs proactive MCPs that improve player understanding.
    Returns list of actions taken / warnings.
    """
    needed = _tracked_by_values() | set(PROACTIVE)
    current = _load_mcp()
    log = []

    for key in needed:
        entry = REGISTRY.get(key)
        if entry is None:
            log.append(f"⚠  no registry entry for tracked_by: {key}")
            continue

        # resolve refs (e.g. calendar_mcp → apple)
        if "ref" in entry:
            ref_key = entry["ref"]
            ref_entry = REGISTRY.get(ref_key)
            if ref_entry and ref_key not in current:
                current[ref_key] = {k: v for k, v in ref_entry.items()
                                    if k not in ("needs_auth", "env_required", "note")}
                log.append(f"✓  added {ref_key} (covers {key})")
            continue

        server_name = key.replace("_mcp", "").replace("_", "-")
        if server_name in current:
            continue

        # check for required env vars
        env_required = entry.get("env_required", [])
        missing_env = [e for e in env_required if not _env_set(e)]
        if missing_env:
            note = entry.get("note", "")
            log.append(f"⚠  {server_name}: needs env vars {missing_env}  —  {note}")
            _queue_credential_task(server_name, missing_env, note)
            continue

        clean = {k: v for k, v in entry.items()
                 if k not in ("needs_auth", "env_required", "note", "ref")}
        current[server_name] = clean
        _save_mcp(current)
        log.append(f"✓  wired {server_name}")

        if "needs_auth" in entry:
            log.append(f"   → run to authorize: {entry['needs_auth']}")

    _save_mcp(current)
    return log


def _queue_credential_task(server_name: str, missing_env: list[str], note: str) -> None:
    import sys
    sys.path.insert(0, str(MEGAMIND))
    from brain.updates import queue_task
    queue_task(
        task_id=f"mcp_cred_{server_name}",
        label=f"Connect {server_name} MCP — add credentials",
        acceptance=f"Env vars set in ~/.megamind.env: {', '.join(missing_env)}",
        tree_id=f"setup_{server_name}",
        goal_metric=f"mcp.{server_name}",
        note=note,
    )


def _env_set(key: str) -> bool:
    import os
    if os.environ.get(key):
        return True
    env_file = Path.home() / ".megamind.env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith(f"{key}=") and line.split("=", 1)[1].strip():
                return True
    return False


if __name__ == "__main__":
    results = sync()
    for line in results:
        print(line)
    if not results:
        print("✓  all MCPs current")
