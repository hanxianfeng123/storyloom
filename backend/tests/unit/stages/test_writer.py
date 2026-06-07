import pytest
from storyloom.core.stages.writer import WriterStage
from storyloom.core.contract import StageInput, PipelineContext, StoryBible


class MockProvider:
    async def complete(self, messages, model=None, temperature=0.7, max_tokens=4096):
        from storyloom.providers.base import LLMResponse
        return LLMResponse(
            content="# Chapter 1\n\nIt was a dark and stormy night...",
            model="mock", tokens_in=0, tokens_out=0, latency_ms=0,
        )


@pytest.mark.asyncio
async def test_writer_returns_chapter_content():
    stage = WriterStage(llm_provider=MockProvider())
    inp = StageInput(
        project_id="proj-1",
        chapter_id="## Outline\n1. Opening",
        context=PipelineContext(
            story_bible=StoryBible(title="Test", genre="Fantasy"),
        ),
    )
    output = await stage.execute(inp)
    assert output.content is not None
    assert len(output.content) > 0
    assert output.decision == "approved"
