import pytest
from storyloom.core.stages.continuity import ContinuityStage
from storyloom.core.contract import StageInput, PipelineContext, StoryBible, ChapterSummary


class MockProvider:
    async def complete(self, messages, model=None, temperature=0.7, max_tokens=4096):
        from storyloom.providers.base import LLMResponse
        return LLMResponse(
            content="No inconsistencies found.",
            model="mock", tokens_in=10, tokens_out=5, latency_ms=50,
        )


@pytest.mark.asyncio
async def test_continuity_checks_consistency():
    stage = ContinuityStage(llm_provider=MockProvider())
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
    output = await stage.execute(inp)
    assert output.content is not None
    assert output.decision == "approved"
