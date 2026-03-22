"""
Pull live data from connected MCPs into context/mcp_data.json.
Uses a minimal stdio JSON-RPC client — no Claude session needed.
Runs daily via the ingest cron.
"""

from __future__ import annotations

import json
import subprocess
import threading
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any

MEGAMIND = Path(__file__).parent.parent
OUT_FILE = MEGAMIND / "context" / "mcp_data.json"
MCP_JSON = MEGAMIND / ".mcp.json"


# ── Minimal MCP stdio client ───────────────────────────────────────

class MCPClient:
    def __init__(self, command: str, args: list[str]):
        self.proc = subprocess.Popen(
            [command] + args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        self._id = 0
        self._lock = threading.Lock()
        self._initialized = False

    def _send(self, method: str, params: dict) -> dict | None:
        with self._lock:
            self._id += 1
            msg = json.dumps({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params})
            try:
                self.proc.stdin.write(msg + "\n")
                self.proc.stdin.flush()
                # read until we get a response with matching id
                deadline = time.time() + 10
                while time.time() < deadline:
                    line = self.proc.stdout.readline()
                    if not line:
                        break
                    try:
                        resp = json.loads(line.strip())
                        if resp.get("id") == self._id:
                            return resp
                    except json.JSONDecodeError:
                        continue
            except Exception:
                pass
        return None

    def initialize(self) -> bool:
        resp = self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "megamind", "version": "1.0"},
        })
        self._initialized = resp is not None and "result" in resp
        return self._initialized

    def call(self, tool: str, arguments: dict) -> Any:
        if not self._initialized:
            return None
        resp = self._send("tools/call", {"name": tool, "arguments": arguments})
        if resp and "result" in resp:
            content = resp["result"].get("content", [])
            texts = [c["text"] for c in content if c.get("type") == "text"]
            return "\n".join(texts) if texts else resp["result"]
        return None

    def close(self):
        try:
            self.proc.terminate()
        except Exception:
            pass


# ── Pulls ──────────────────────────────────────────────────────────

def _pull_apple(cfg: dict) -> dict:
    client = MCPClient(cfg["command"], cfg["args"])
    data: dict[str, Any] = {}
    try:
        if not client.initialize():
            return {"error": "failed to initialize"}

        today = date.today().isoformat()

        # Calendar — today's events
        cal = client.call("calendar", {"operation": "list"})
        if cal:
            data["calendar_today"] = cal

        # Messages — recent unread
        msgs = client.call("messages", {"operation": "unread"})
        if msgs:
            data["recent_messages"] = msgs

        # Mail — unread
        mail = client.call("mail", {"operation": "unread"})
        if mail:
            data["apple_mail_unread"] = mail

    finally:
        client.close()
    return data


def _pull_gmail(cfg: dict) -> dict:
    client = MCPClient(cfg["command"], cfg["args"])
    data: dict[str, Any] = {}
    try:
        if not client.initialize():
            return {"error": "failed to initialize"}

        result = client.call("search_emails", {
            "query": "is:unread newer_than:2d",
            "maxResults": 20,
        })
        if result:
            data["gmail_unread"] = result

    finally:
        client.close()
    return data


# ── Main ───────────────────────────────────────────────────────────

def pull() -> dict:
    if not MCP_JSON.exists():
        return {}

    mcp_cfg = json.loads(MCP_JSON.read_text())
    results: dict[str, Any] = {
        "pulled_at": datetime.now().isoformat(),
        "date": date.today().isoformat(),
    }

    apple = mcp_cfg.get("apple")
    if apple:
        print("  pulling apple-mcp...")
        results["apple"] = _pull_apple(apple)

    gmail = mcp_cfg.get("gmail")
    if gmail:
        print("  pulling gmail...")
        results["gmail"] = _pull_gmail(gmail)

    OUT_FILE.write_text(json.dumps(results, indent=2))
    print(f"  saved → {OUT_FILE}")
    return results


if __name__ == "__main__":
    pull()
