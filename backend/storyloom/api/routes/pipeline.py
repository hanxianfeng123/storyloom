from fastapi import APIRouter, Depends, HTTPException
from storyloom.core.pipeline import PipelineOrchestrator
from storyloom.memory.store import SQLiteStore
from storyloom.api.deps import get_store

router = APIRouter()
_active_pipelines: dict[str, PipelineOrchestrator] = {}


@router.post("/start")
async def start_pipeline(project_id: str, chapter: int, store: SQLiteStore = Depends(get_store)):
    from storyloom.core.stages.planner import PlannerStage
    from storyloom.core.stages.writer import WriterStage
    from storyloom.core.stages.editor import EditorStage
    from storyloom.core.stages.quality_gate import QualityGateStage

    stages = [
        PlannerStage(llm_provider=None),  # Will use real provider from config
        WriterStage(llm_provider=None),
        EditorStage(llm_provider=None),
        QualityGateStage(),
    ]
    orch = PipelineOrchestrator(stages=stages)
    pipeline_id = f"{project_id}:ch{chapter}"
    _active_pipelines[pipeline_id] = orch
    return {"pipeline_id": pipeline_id, "status": "started"}


@router.get("/status/{pipeline_id}")
async def get_status(pipeline_id: str):
    orch = _active_pipelines.get(pipeline_id)
    if not orch:
        raise HTTPException(404, "Pipeline not found")
    return {"pipeline_id": pipeline_id, "status": "running"}


@router.post("/cancel/{pipeline_id}")
async def cancel_pipeline(pipeline_id: str):
    orch = _active_pipelines.get(pipeline_id)
    if not orch:
        raise HTTPException(404, "Pipeline not found")
    await orch.cancel()
    return {"status": "cancelled"}
