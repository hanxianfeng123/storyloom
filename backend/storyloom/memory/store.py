import aiosqlite
from typing import Optional
from storyloom.memory.models.character import Character
from storyloom.memory.models.plot_thread import PlotThread
from storyloom.memory.models.world_state import WorldStateEntry
from storyloom.memory.models.chapter import ChapterRecord
from storyloom.core.errors import MemoryError
from pathlib import Path


class SQLiteStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self):
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._run_migrations()

    async def _run_migrations(self):
        mig_dir = Path(__file__).parent / "migrations"
        for f in sorted(mig_dir.glob("*.sql")):
            sql = f.read_text()
            await self._conn.executescript(sql)
        await self._conn.commit()

    async def save_character(self, project_id: str, char: Character) -> None:
        await self._conn.execute(
            """INSERT OR REPLACE INTO characters
               (project_id, name, role, personality, appearance, background,
                location, status, emotional_arc, last_seen_chapter, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, char.name, char.role, char.personality, char.appearance,
             char.background, char.location, char.status, char.emotional_arc,
             char.last_seen_chapter, char.notes),
        )
        await self._conn.commit()

    async def get_character(self, project_id: str, name: str) -> Optional[Character]:
        cursor = await self._conn.execute(
            "SELECT * FROM characters WHERE project_id = ? AND name = ?",
            (project_id, name),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return Character(**dict(row))

    async def list_characters(self, project_id: str) -> list[Character]:
        cursor = await self._conn.execute(
            "SELECT * FROM characters WHERE project_id = ? ORDER BY name",
            (project_id,),
        )
        rows = await cursor.fetchall()
        return [Character(**dict(r)) for r in rows]

    async def save_plot_thread(self, project_id: str, thread: PlotThread) -> None:
        await self._conn.execute(
            """INSERT OR REPLACE INTO plot_threads
               (project_id, name, status, first_chapter, target_chapter, last_seen_chapter, description)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (project_id, thread.name, thread.status, thread.first_chapter,
             thread.target_chapter, thread.last_seen_chapter, thread.description),
        )
        await self._conn.commit()

    async def list_plot_threads(self, project_id: str) -> list[PlotThread]:
        cursor = await self._conn.execute(
            "SELECT * FROM plot_threads WHERE project_id = ? ORDER BY name",
            (project_id,),
        )
        rows = await cursor.fetchall()
        return [PlotThread(**dict(r)) for r in rows]

    async def set_world_state(self, project_id: str, entry: WorldStateEntry) -> None:
        await self._conn.execute(
            """INSERT OR REPLACE INTO world_state (project_id, key, value, chapter_number, updated_at)
               VALUES (?, ?, ?, ?, ?)""",
            (project_id, entry.key, entry.value, entry.chapter_number, entry.updated_at),
        )
        await self._conn.commit()

    async def get_world_state(self, project_id: str, key: str) -> Optional[WorldStateEntry]:
        cursor = await self._conn.execute(
            "SELECT * FROM world_state WHERE project_id = ? AND key = ?",
            (project_id, key),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return WorldStateEntry(**dict(row))

    async def save_chapter(self, project_id: str, chapter: ChapterRecord) -> None:
        await self._conn.execute(
            """INSERT OR REPLACE INTO chapters
               (project_id, number, title, status, word_count, summary, outline, draft_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, chapter.number, chapter.title, chapter.status,
             chapter.word_count, chapter.summary, chapter.outline, chapter.draft_path),
        )
        await self._conn.commit()

    async def get_chapter(self, project_id: str, number: int) -> Optional[ChapterRecord]:
        cursor = await self._conn.execute(
            "SELECT * FROM chapters WHERE project_id = ? AND number = ?",
            (project_id, number),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return ChapterRecord(**dict(row))

    async def log_operation(self, project_id: str, pipeline_id: str, stage: str,
                            model: str, tokens_in: int, tokens_out: int,
                            latency_ms: int, result: str) -> None:
        await self._conn.execute(
            """INSERT INTO operation_logs
               (project_id, pipeline_id, stage, model, tokens_in, tokens_out, latency_ms, result)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, pipeline_id, stage, model, tokens_in, tokens_out, latency_ms, result),
        )
        await self._conn.commit()

    def close(self):
        if self._conn:
            import asyncio
            asyncio.create_task(self._conn.close())
