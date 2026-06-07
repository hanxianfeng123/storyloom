from fastapi import APIRouter, Depends
from storyloom.memory.store import SQLiteStore
from storyloom.api.deps import get_store

router = APIRouter()


@router.get("/{project_id}")
async def list_chapters(project_id: str, store: SQLiteStore = Depends(get_store)):
    return {"chapters": []}


@router.get("/{project_id}/{number}")
async def get_chapter(project_id: str, number: int, store: SQLiteStore = Depends(get_store)):
    chapter = await store.get_chapter(project_id, number)
    if not chapter:
        return {"chapter": None}
    return {"chapter": chapter.model_dump()}
