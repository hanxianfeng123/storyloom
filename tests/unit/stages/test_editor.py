import pytest
from storyloom.core.stages.editor import EditorStage
from storyloom.core.contract import StageInput, PipelineContext, StoryBible


class MockProvider:
    async def complete(self, messages, model=None, temperature=0.7, max_tokens=4096):
        from storyloom.providers.base import LLMResponse
        return LLMResponse(
            content="This is the revised chapter text.",
            model="mock", tokens_in=10, tokens_out=5, latency_ms=50,
        )


@pytest.mark.asyncio
async def test_editor_returns_revised_content():
    stage = EditorStage(llm_provider=MockProvider())
    inp = StageInput(
        project_id="proj-1",
        chapter_id="Original chapter text with some issues.",
        context=PipelineContext(
            story_bible=StoryBible(title="Test", genre="Fantasy"),
        ),
    )
    output = await stage.execute(inp)
    assert output.content is not None
    assert "Editor Change Log" in output.content
    assert output.decision == "approved"
