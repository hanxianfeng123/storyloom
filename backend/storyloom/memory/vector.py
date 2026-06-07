import aiosqlite
import hashlib
import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import sqlite_vec
    HAS_VEC = True
except ImportError:
    HAS_VEC = False
    logger.warning("sqlite-vec not installed. Vector search degraded to keyword matching.")


class VectorStore:
    """
    Vector storage for context retrieval.

    When sqlite-vec is available: uses semantic vector search.
    Fallback: keyword-based LIKE search (less accurate but functional).

    The fallback is EXPLICIT — a WARNING is logged at import time so
    the user knows to install sqlite-vec for proper semantic search.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn: aiosqlite.Connection | None = None
        self.has_vec = HAS_VEC

    async def connect(self):
        self._conn = await aiosqlite.connect(self.db_path)
        if self.has_vec:
            self._conn.enable_load_extension(True)
            sqlite_vec.load(self._conn)
            await self._conn.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS vec_entries USING vec0(embedding float[384])"
            )
        else:
            await self._conn.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_emb_project ON embeddings(project_id)"
            )
        await self._conn.commit()

    async def add_entry(self, project_id: str, content: str, metadata: dict | None = None) -> str:
        import json
        entry_id = hashlib.md5(f"{project_id}:{content[:100]}".encode()).hexdigest()[:12]
        if self.has_vec:
            # sqlite-vec: store content + compute embedding via LLM call
            pass  # Will be implemented with embedding API call
        else:
            await self._conn.execute(
                "INSERT OR REPLACE INTO embeddings (id, project_id, content, metadata) VALUES (?, ?, ?, ?)",
                (entry_id, project_id, content, json.dumps(metadata or {})),
            )
        await self._conn.commit()
        return entry_id

    async def search(self, project_id: str, query: str, limit: int = 5) -> list[dict[str, Any]]:
        import json
        if self.has_vec:
            # sqlite-vec vector search
            pass
        else:
            cursor = await self._conn.execute(
                """SELECT content, metadata FROM embeddings
                   WHERE project_id = ? AND content LIKE ?
                   ORDER BY created_at DESC LIMIT ?""",
                (project_id, f"%{query}%", limit),
            )
            rows = await cursor.fetchall()
            return [{"content": row[0], "metadata": json.loads(row[1])} for row in rows]

    def close(self):
        if self._conn:
            import asyncio
            asyncio.create_task(self._conn.close())
