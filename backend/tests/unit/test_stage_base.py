import pytest
from storyloom.core.stages.base import Stage
from storyloom.core.contract import StageInput, StageOutput, PipelineContext, StageMetrics, StoryBible


class ConcreteStage(Stage):
    name = "test_stage"

    async def execute(self, input: StageInput) -> StageOutput:
        return StageOutput(
            content="test output",
            decision="approved",
            metrics=StageMetrics(model="test", tokens_in=0, tokens_out=0, latency_ms=0, cost_usd=0),
        )


@pytest.mark.asyncio
async def test_stage_execute():
    stage = ConcreteStage()
    inp = StageInput(
        project_id="proj-1",
        context=PipelineContext(story_bible=StoryBible(title="Test", genre="Fantasy")),
    )
    output = await stage.execute(inp)
    assert output.content == "test output"
    assert output.decision == "approved"
    assert stage.name == "test_stage"
