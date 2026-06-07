from functools import lru_cache
from storyloom.memory.store import SQLiteStore
from storyloom.core.pipeline import PipelineOrchestrator
from storyloom.config.settings import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()


async def get_store() -> SQLiteStore:
    settings = get_settings()
    db_path = settings.database_url.replace("sqlite:///", "")
    store = SQLiteStore(db_path)
    await store.connect()
    return store
