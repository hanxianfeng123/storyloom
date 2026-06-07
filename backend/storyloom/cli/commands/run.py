import asyncio
import typer
from storyloom.memory.store import SQLiteStore
from storyloom.providers.router import ProviderRouter
from storyloom.providers.openai import OpenAIProvider
from storyloom.providers.anthropic import AnthropicProvider
from storyloom.providers.deepseek import DeepSeekProvider
from storyloom.core.pipeline import PipelineOrchestrator
from storyloom.core.stages.planner import PlannerStage
from storyloom.core.stages.writer import WriterStage
from storyloom.core.stages.editor import EditorStage
from storyloom.core.stages.continuity import ContinuityStage
from storyloom.core.stages.quality_gate import QualityGateStage
from storyloom.core.contract import PipelineContext, StoryBible
from storyloom.config.settings import Settings


def parse_chapter_spec(chapter: str) -> list[int]:
    """Parse '3' -> [3], '3-5' -> [3,4,5]."""
    if "-" in chapter:
        start, end = chapter.split("-")
        return list(range(int(start), int(end) + 1))
    return [int(chapter)]


def run_pipeline(chapter: str):
    """Run pipeline for chapter(s). Format: '3' or '3-5'."""
    settings = Settings()
    chapters = parse_chapter_spec(chapter)

    async def _run():
        store = SQLiteStore("storyloom.db")
        await store.connect()

        router = ProviderRouter()
        if "openai" in settings.llm_providers:
            router.register(
                "gpt-4o",
                "openai",
                OpenAIProvider(api_key=settings.llm_providers["openai"]["api_key"]),
            )
        if "anthropic" in settings.llm_providers:
            router.register(
                "claude-sonnet",
                "anthropic",
                AnthropicProvider(api_key=settings.llm_providers["anthropic"]["api_key"]),
            )
        if "deepseek" in settings.llm_providers:
            router.register(
                "deepseek-chat",
                "deepseek",
                DeepSeekProvider(api_key=settings.llm_providers["deepseek"]["api_key"]),
            )

        _, planner_provider = router.select("planner", "zh")
        _, writer_provider = router.select("writer", "zh")

        stages = [
            PlannerStage(llm_provider=planner_provider),
            WriterStage(llm_provider=writer_provider),
            EditorStage(llm_provider=planner_provider),
            ContinuityStage(llm_provider=planner_provider),
            QualityGateStage(),
        ]

        orch = PipelineOrchestrator(stages=stages)
        for ch in chapters:
            typer.echo(f"Generating chapter {ch}...")
            ctx = PipelineContext(story_bible=StoryBible(title="", genre=""))
            result = await orch.run(project_id="default", chapter_id=str(ch), context=ctx)
            typer.echo(f"  -> {result.status}")

    asyncio.run(_run())
