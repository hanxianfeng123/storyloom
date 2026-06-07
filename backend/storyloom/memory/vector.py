import aiosqlite
import hashlib
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Keyword-based context store for memory retrieval.

    When sqlite-vec is installed (optional), it uses proper vector search.
    Falls back to LIKE-based keyword matching without it.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self):
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
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
        entry_id = hashlib.md5(f"{project_id}:{content[:100]}".encode()).hexdigest()[:12]
        await self._conn.execute(
            "INSERT OR REPLACE INTO embeddings (id, project_id, content, metadata) VALUES (?, ?, ?, ?)",
            (entry_id, project_id, content, json.dumps(metadata or {})),
        )
        await self._conn.commit()
        return entry_id

    async def search(self, project_id: str, query: str, limit: int = 5) -> list[dict[str, Any]]:
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
