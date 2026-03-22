"""
Megamind memory layer.
Abstracts over local (SQLite + sentence-transformers) and cloud (mem0) backends.

Mode is set in config/player.yaml → memory_mode: local | cloud

LOCAL MODE
  - SQLite for storage (already present, zero setup)
  - sentence-transformers for embeddings (pip install, ~100MB one-time download)
  - cosine similarity for search
  - Zero services. Zero API keys. Everything on this machine.

CLOUD MODE
  - mem0 MemoryClient
  - Requires MEM0_API_KEY in .env
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import yaml

MEGAMIND = Path(__file__).parent.parent
PLAYER_FILE = MEGAMIND / "config" / "player.yaml"
DB_PATH = MEGAMIND / "db" / "megamind.db"
MEMORY_DB = MEGAMIND / "db" / "memory.db"


def _get_mode() -> str:
    try:
        config = yaml.safe_load(PLAYER_FILE.read_text())
        return config.get("memory_mode", "local")
    except Exception:
        return "local"


def _get_user_id() -> str:
    try:
        config = yaml.safe_load(PLAYER_FILE.read_text())
        return config.get("name", "player")
    except Exception:
        return "player"


# ─── Local backend ────────────────────────────────────────────

class LocalMemory:
    """
    SQLite + sentence-transformers memory.
    Zero services. Zero API keys. Everything on disk.
    """

    MODEL_NAME = "all-MiniLM-L6-v2"  # 80MB, fast, good quality

    def __init__(self):
        self._model = None
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(MEMORY_DB)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   TEXT NOT NULL,
                content   TEXT NOT NULL,
                embedding BLOB,
                metadata  TEXT,
                created_at DATETIME DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
        conn.close()

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.MODEL_NAME)
            except ImportError:
                raise ImportError(
                    "Local memory requires sentence-transformers.\n"
                    "Run: pip install sentence-transformers"
                )
        return self._model

    def _embed(self, text: str) -> list[float]:
        model = self._get_model()
        return model.encode(text).tolist()

    def add(self, content: str, user_id: str = "player", metadata: dict | None = None) -> dict:
        embedding = self._embed(content)
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.execute(
            "INSERT INTO memories (user_id, content, embedding, metadata) VALUES (?, ?, ?, ?)",
            (user_id, content, json.dumps(embedding), json.dumps(metadata or {})),
        )
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        return {"id": row_id, "memory": content}

    def search(self, query: str, user_id: str = "player", limit: int = 5) -> list[dict]:
        import math

        query_emb = self._embed(query)
        conn = sqlite3.connect(MEMORY_DB)
        rows = conn.execute(
            "SELECT id, content, embedding FROM memories WHERE user_id = ?",
            (user_id,),
        ).fetchall()
        conn.close()

        def cosine(a: list[float], b: list[float]) -> float:
            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a))
            nb = math.sqrt(sum(x * x for x in b))
            return dot / (na * nb + 1e-9)

        scored = []
        for row_id, content, emb_json in rows:
            try:
                emb = json.loads(emb_json)
                score = cosine(query_emb, emb)
                scored.append({"id": row_id, "memory": content, "score": score})
            except Exception:
                continue

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    def get_all(self, user_id: str = "player") -> list[dict]:
        conn = sqlite3.connect(MEMORY_DB)
        rows = conn.execute(
            "SELECT id, content, metadata, created_at FROM memories WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        conn.close()
        return [{"id": r[0], "memory": r[1], "metadata": r[2], "created_at": r[3]} for r in rows]


# ─── Cloud backend ────────────────────────────────────────────

class CloudMemory:
    """mem0 cloud API backend. Requires MEM0_API_KEY."""

    def __init__(self):
        from mem0 import MemoryClient
        self._client = MemoryClient()

    def add(self, content: str, user_id: str = "player", metadata: dict | None = None) -> dict:
        return self._client.add(content, user_id=user_id, metadata=metadata or {})

    def search(self, query: str, user_id: str = "player", limit: int = 5) -> list[dict]:
        return self._client.search(query, user_id=user_id, limit=limit)

    def get_all(self, user_id: str = "player") -> list[dict]:
        return self._client.get_all(user_id=user_id)


# ─── Unified interface ────────────────────────────────────────

class Memory:
    """
    Single interface for both backends.
    Switch via config/player.yaml → memory_mode: local | cloud
    """

    def __init__(self):
        mode = _get_mode()
        if mode == "cloud":
            self._backend = CloudMemory()
        else:
            self._backend = LocalMemory()
        self._user_id = _get_user_id()

    def add(self, content: str, metadata: dict | None = None) -> dict:
        return self._backend.add(content, user_id=self._user_id, metadata=metadata)

    def search(self, query: str, limit: int = 5) -> list[dict]:
        return self._backend.search(query, user_id=self._user_id, limit=limit)

    def get_all(self) -> list[dict]:
        return self._backend.get_all(user_id=self._user_id)


# ─── Convenience ─────────────────────────────────────────────

def get_memory() -> Memory:
    """Get a memory instance configured for the current player."""
    return Memory()
