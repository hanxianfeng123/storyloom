from fastapi import APIRouter, Depends
from storyloom.memory.store import SQLiteStore
from storyloom.api.deps import get_store

router = APIRouter()


@router.get("/characters/{project_id}")
async def list_characters(project_id: str, store: SQLiteStore = Depends(get_store)):
    chars = await store.list_characters(project_id)
    return {"characters": [c.model_dump() for c in chars]}


@router.get("/plot-threads/{project_id}")
async def list_plot_threads(project_id: str, store: SQLiteStore = Depends(get_store)):
    threads = await store.list_plot_threads(project_id)
    return {"plot_threads": [t.model_dump() for t in threads]}
