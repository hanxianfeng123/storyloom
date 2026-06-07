import asyncio
import typer
from storyloom.memory.store import SQLiteStore
from storyloom.memory.skill_store import SkillStore
from storyloom.core.pipeline import PipelineOrchestrator
from storyloom.core.skills.registry import SkillRegistry
from storyloom.core.skills.engine import SkillExecutionEngine
from storyloom.core.skills.supervisor import SupervisorPipeline, SupervisorConfig
from storyloom.core.contract import PipelineContext, StoryBible


def parse_chapter_spec(chapter: str) -> list[int]:
    """Parse '3' -> [3], '3-5' -> [3,4,5]."""
    if "-" in chapter:
        start, end = chapter.split("-")
        return list(range(int(start), int(end) + 1))
    return [int(chapter)]


def run_pipeline(chapter: str, legacy: bool = False):
    """Run pipeline for chapter(s). Format: '3' or '3-5'.

    Defaults to the LLM-driven supervisor pipeline.
    Use --legacy to use the old hardcoded stage pipeline.
    """
    chapters = parse_chapter_spec(chapter)

    async def _run():
        store = SQLiteStore("storyloom.db")
        await store.connect()
        conn = store.connection
        if conn is None:
            raise RuntimeError("Database not connected")
        skill_store = SkillStore(conn)

        ctx = PipelineContext(
            project_id="default",
            story_bible=StoryBible(title="", genre=""),
        )

        for ch in chapters:
            ctx.chapter_number = ch

            if legacy:
                from storyloom.core.stages.planner import PlannerStage
                from storyloom.core.stages.writer import WriterStage
                from storyloom.core.stages.editor import EditorStage
                from storyloom.core.stages.continuity import ContinuityStage
                from storyloom.core.stages.quality_gate import QualityGateStage

                stages = [
                    PlannerStage(),
                    WriterStage(),
                    EditorStage(),
                    ContinuityStage(),
                    QualityGateStage(),
                ]
                orch = PipelineOrchestrator(stages=stages)
                result = await orch.run(
                    project_id="default", chapter_id=str(ch), context=ctx
                )
            else:
                registry = SkillRegistry(skill_store)
                await registry.load_from_db()
                engine = SkillExecutionEngine(skill_store, registry)
                supervisor = SupervisorPipeline(
                    engine, registry, skill_store, SupervisorConfig()
                )
                orch = PipelineOrchestrator(supervisor_pipeline=supervisor)
                result = await orch.run(
                    project_id="default", context=ctx, use_supervisor=True
                )

            typer.echo(f"Chapter {ch}: {result.status}")
            if hasattr(result, "skill_log") and result.skill_log:
                for s in result.skill_log:
                    typer.echo(f"  Step {s.step}: {s.skill_name} ({s.status})")
            if hasattr(result, "stage_results") and result.stage_results:
                for r in result.stage_results:
                    typer.echo(f"  {r['stage']}: {r['decision']}")

    asyncio.run(_run())
