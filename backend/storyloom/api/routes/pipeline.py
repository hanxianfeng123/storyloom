from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from storyloom.core.pipeline import PipelineOrchestrator
from storyloom.core.contract import PipelineContext, StoryBible
from storyloom.memory.store import SQLiteStore
from storyloom.core.task_queue import TaskQueue
from storyloom.api.deps import get_store, get_registry, get_engine, get_skill_store

router = APIRouter()
_active_pipelines: dict[str, dict] = {}
_queue = TaskQueue()


@router.post("/start")
async def start_pipeline(
    project_id: str,
    chapter: int = Query(1),
    legacy: bool = Query(False, description="Use old hardcoded stage pipeline"),
    store: SQLiteStore = Depends(get_store),
    registry=Depends(get_registry),
    engine=Depends(get_engine),
    skill_store=Depends(get_skill_store),
):
    """Start a pipeline run. Defaults to LLM-driven supervisor pipeline."""
    ctx = PipelineContext(
        project_id=project_id,
        chapter_number=chapter,
        story_bible=StoryBible(title="", genre="fiction"),
    )

    if legacy:
        from storyloom.core.stages.planner import PlannerStage
        from storyloom.core.stages.writer import WriterStage
        from storyloom.core.stages.editor import EditorStage
        from storyloom.core.stages.quality_gate import QualityGateStage

        stages = [
            PlannerStage(llm_provider=None),
            WriterStage(llm_provider=None),
            EditorStage(llm_provider=None),
            QualityGateStage(),
        ]
        orch = PipelineOrchestrator(stages=stages)
        task = await _queue.submit(
            orch.run(project_id, chapter_id=str(chapter), context=ctx)
        )
        pipeline_type = "legacy"
    else:
        from storyloom.core.skills.supervisor import SupervisorPipeline, SupervisorConfig

        supervisor = SupervisorPipeline(engine, registry, skill_store, SupervisorConfig())
        orch = PipelineOrchestrator(supervisor_pipeline=supervisor)
        task = await _queue.submit(
            orch.run(project_id, context=ctx, use_supervisor=True)
        )
        pipeline_type = "supervisor"

    _active_pipelines[task.id] = {"orch": orch, "task": task, "type": pipeline_type}
    return {"pipeline_id": task.id, "status": "started", "type": pipeline_type}


@router.get("/status/{pipeline_id}")
async def get_status(pipeline_id: str):
    info = _active_pipelines.get(pipeline_id)
    if not info:
        raise HTTPException(404, "Pipeline not found")

    task = info["task"]
    result: dict = {"pipeline_id": pipeline_id, "status": task.status}

    if task.status == "running":
        return result

    if task.status == "failed":
        result["error"] = task.error
        return result

    if task.result is None:
        return result

    pipeline_result = task.result
    # Supervisor result → extract skill log as stage_results
    skill_log = getattr(pipeline_result, "skill_log", [])
    if skill_log:
        result["stage_results"] = [
            {"stage": s.skill_name, "decision": s.status} for s in skill_log
        ]
        result["chapter_content"] = getattr(pipeline_result, "chapter_content", None)
        result["total_steps"] = len(skill_log)
        result["total_cost_usd"] = getattr(pipeline_result, "total_cost_usd", 0)
    else:
        # Legacy result
        stage_results = getattr(pipeline_result, "stage_results", [])
        if stage_results:
            result["stage_results"] = stage_results

    return result


@router.post("/cancel/{pipeline_id}")
async def cancel_pipeline(pipeline_id: str):
    info = _active_pipelines.get(pipeline_id)
    if not info:
        raise HTTPException(404, "Pipeline not found")
    await info["orch"].cancel()
    return {"status": "cancelled"}


class SupervisorRunRequest(BaseModel):
    project_id: str = "test"
    chapter_number: int = 1
    title: str = "Untitled"
    genre: str = "fiction"
    chapter_content: str | None = None
    current_outline: str | None = None
    supervisor_instructions: str | None = None


@router.post("/supervisor")
async def run_supervisor(
    req: SupervisorRunRequest,
    registry=Depends(get_registry),
    engine=Depends(get_engine),
    store=Depends(get_skill_store),
):
    """Run supervisor pipeline synchronously (for testing)."""
    from storyloom.core.skills.supervisor import SupervisorPipeline, SupervisorConfig

    ctx = PipelineContext(
        project_id=req.project_id,
        chapter_number=req.chapter_number,
        story_bible=StoryBible(title=req.title, genre=req.genre),
        chapter_content=req.chapter_content,
        current_outline=req.current_outline,
        supervisor_instructions=req.supervisor_instructions,
    )
    pipeline = SupervisorPipeline(engine, registry, store, SupervisorConfig())
    result = await pipeline.run(ctx)
    return result
