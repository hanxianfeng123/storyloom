from fastapi import APIRouter, Depends, HTTPException
from storyloom.core.contract import PipelineContext, StoryBible
from storyloom.core.skills.registry import SkillRegistry
from storyloom.core.skills.engine import SkillExecutionEngine
from storyloom.api.deps import get_registry, get_engine
from pydantic import BaseModel

router = APIRouter()


@router.get("/")
async def list_skills(registry: SkillRegistry = Depends(get_registry)):
    """Return skill tree for navigation / selection."""
    return {"tree": registry.tree(), "active": registry.list_active()}


@router.get("/{name}")
async def get_skill(name: str, registry: SkillRegistry = Depends(get_registry)):
    skill = registry.get(name)
    if not skill:
        raise HTTPException(404, f"Skill '{name}' not found")
    return skill


class SkillUpdateBody(BaseModel):
    description: str | None = None
    system_prompt: str | None = None
    user_prompt_template: str | None = None
    post_process_template: str | None = None
    model: str | None = None
    fallback_model: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    is_active: bool | None = None
    change_note: str = ""


@router.put("/{name}")
async def update_skill(
    name: str,
    update: SkillUpdateBody,
    registry: SkillRegistry = Depends(get_registry),
):
    """Update skill fields (system_prompt, model, temperature, etc.)."""
    skill = registry.get(name)
    if not skill:
        raise HTTPException(404, f"Skill '{name}' not found")

    from storyloom.memory.models.skill import SkillUpdate as SkillUpdateModel

    updated = await registry._store.update_skill(
        skill["id"],
        SkillUpdateModel(**update.model_dump(exclude_none=True)),
    )
    if updated:
        await registry.reload_skill(name)
    return updated or skill


@router.get("/{name}/versions")
async def get_skill_versions(name: str, registry: SkillRegistry = Depends(get_registry)):
    skill = registry.get(name)
    if not skill:
        raise HTTPException(404, f"Skill '{name}' not found")
    return {"versions": await registry._store.get_skill_versions(skill["id"])}


@router.post("/{name}/rollback")
async def rollback_skill(
    name: str,
    target_version: int,
    registry: SkillRegistry = Depends(get_registry),
):
    skill = registry.get(name)
    if not skill:
        raise HTTPException(404, f"Skill '{name}' not found")
    updated = await registry._store.rollback_skill(skill["id"], target_version)
    if not updated:
        raise HTTPException(404, f"Version {target_version} not found")
    await registry.reload_skill(name)
    return updated


@router.get("/{name}/runs")
async def list_skill_runs(name: str, registry: SkillRegistry = Depends(get_registry)):
    skill = registry.get(name)
    if not skill:
        raise HTTPException(404, f"Skill '{name}' not found")
    return {"runs": await registry._store.list_runs("", None)}


class ExecuteRequest(BaseModel):
    project_id: str = "test"
    chapter_number: int = 1
    rationale: str = ""
    chapter_content: str | None = None
    current_outline: str | None = None
    supervisor_instructions: str | None = None


@router.post("/{name}/execute")
async def execute_skill(
    name: str,
    req: ExecuteRequest,
    engine: SkillExecutionEngine = Depends(get_engine),
):
    """Execute a single skill for testing purposes. Does not update pipeline state."""
    ctx = PipelineContext(
        project_id=req.project_id,
        chapter_number=req.chapter_number,
        story_bible=StoryBible(title="Test", genre="fiction"),
        chapter_content=req.chapter_content,
        current_outline=req.current_outline,
        supervisor_instructions=req.supervisor_instructions,
    )
    try:
        result = await engine.execute(
            skill_name=name,
            context=ctx,
            rationale=req.rationale,
        )
        return result
    except ValueError as e:
        raise HTTPException(404, str(e))
