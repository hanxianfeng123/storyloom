from functools import lru_cache
from storyloom.memory.store import SQLiteStore
from storyloom.memory.skill_store import SkillStore
from storyloom.core.skills.registry import SkillRegistry
from storyloom.core.skills.engine import SkillExecutionEngine
from storyloom.config.settings import Settings

_store: SQLiteStore | None = None
_registry: SkillRegistry | None = None
_engine: SkillExecutionEngine | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


async def get_store() -> SQLiteStore:
    global _store
    if _store is None:
        settings = get_settings()
        db_path = settings.database_url.replace("sqlite:///", "")
        _store = SQLiteStore(db_path)
        await _store.connect()
    return _store


async def get_skill_store() -> SkillStore:
    store = await get_store()
    conn = store.connection
    if conn is None:
        raise RuntimeError("Database not connected")
    return SkillStore(conn)


async def get_registry() -> SkillRegistry:
    global _registry
    if _registry is None:
        skill_store = await get_skill_store()
        _registry = SkillRegistry(skill_store)
        await _registry.load_from_db()
    return _registry


async def get_engine() -> SkillExecutionEngine:
    global _engine
    if _engine is None:
        skill_store = await get_skill_store()
        registry = await get_registry()
        _engine = SkillExecutionEngine(skill_store, registry)
    return _engine
