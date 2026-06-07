import pytest
from storyloom.core.stages.planner import PlannerStage
from storyloom.core.contract import StageInput, PipelineContext, StoryBible, StageOutput


class MockProvider:
    async def complete(self, messages, model=None, temperature=0.7, max_tokens=4096):
        from storyloom.providers.base import LLMResponse
        return LLMResponse(
            content="## 章节细纲\n1. 开场场景\n2. 冲突升级\n3. 转折",
            model="mock", tokens_in=0, tokens_out=0, latency_ms=0,
        )


@pytest.mark.asyncio
async def test_planner_requires_outline_in_output():
    stage = PlannerStage(llm_provider=MockProvider())
    inp = StageInput(
        project_id="proj-1",
        context=PipelineContext(
            story_bible=StoryBible(title="Test", genre="Fantasy", summary="A hero's journey"),
        ),
    )
    output = await stage.execute(inp)
    assert output.content is not None
    assert len(output.content) > 0
    assert output.decision == "approved"
