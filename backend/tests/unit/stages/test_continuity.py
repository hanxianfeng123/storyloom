import pytest
from unittest.mock import patch, AsyncMock
from storyloom.core.stages.continuity import ContinuityStage
from storyloom.core.contract import StageInput, PipelineContext, StoryBible, ChapterSummary


@pytest.mark.asyncio
async def test_continuity_checks_consistency():
    mock_response = AsyncMock()
    mock_response.content = "No inconsistencies found."
    mock_response.model = "mock"
    mock_response.tokens_in = 10
    mock_response.tokens_out = 5
    mock_response.latency_ms = 50

    with patch("storyloom.providers.litellm.complete", new_callable=AsyncMock, return_value=mock_response):
        inp = StageInput(
            project_id="proj-1",
            chapter_id="Chapter text here...",
            context=PipelineContext(
                story_bible=StoryBible(title="Test", genre="Fantasy"),
                chapter_history=[
                    ChapterSummary(number=1, title="Ch1", summary="The hero begins their journey."),
                ],
            ),
        )
        output = await ContinuityStage.execute(inp)
        assert output.content is not None
        assert output.decision == "approved"
