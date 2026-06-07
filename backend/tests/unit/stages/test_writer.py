import pytest
from unittest.mock import patch, AsyncMock
from storyloom.core.stages.writer import WriterStage
from storyloom.core.contract import StageInput, PipelineContext, StoryBible
from storyloom.providers.litellm import LLMResponse


@pytest.mark.asyncio
async def test_writer_returns_chapter_content():
    mock_response = LLMResponse(
        content="# Chapter 1\n\nIt was a dark and stormy night...",
        model="mock",
        tokens_in=50,
        tokens_out=10,
        latency_ms=100,
    )

    # Patch where 'complete' is used: storyloom.core.stages.base (LLMStage imports it)
    with patch("storyloom.core.stages.base.complete", new_callable=AsyncMock, return_value=mock_response):
        inp = StageInput(
            project_id="proj-1",
            chapter_id="## Outline\n1. Opening",
            context=PipelineContext(
                story_bible=StoryBible(title="Test", genre="Fantasy"),
            ),
        )
        output = await WriterStage.execute(inp)
        assert output.content is not None
        assert len(output.content) > 0
        assert output.decision == "approved"
        assert output.metrics.model == "mock"
