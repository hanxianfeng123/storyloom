from fastapi import APIRouter, Depends
from storyloom.memory.store import SQLiteStore
from storyloom.api.deps import get_store

router = APIRouter()


@router.get("/")
async def list_projects(store: SQLiteStore = Depends(get_store)):
    # Query distinct project_ids from chapters table
    return {"projects": []}


@router.post("/")
async def create_project(name: str, store: SQLiteStore = Depends(get_store)):
    return {"name": name, "status": "created"}
