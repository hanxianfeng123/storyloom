import pytest
from storyloom.core.stages.base import Stage, LLMStage
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


def test_llm_stage_build_messages():
    stage = LLMStage(
        name="test_llm",
        system_prompt="You are a test assistant.",
        model="test-model",
        build_user_prompt=lambda inp: f"User prompt for {inp.project_id}",
    )
    inp = StageInput(
        project_id="proj-1",
        context=PipelineContext(story_bible=StoryBible(title="Test", genre="Fantasy")),
    )
    messages = stage.build_messages(inp)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are a test assistant."
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "User prompt for proj-1"


def test_llm_stage_default_user_prompt():
    stage = LLMStage(name="test", system_prompt="", model="test-model")
    inp = StageInput(
        project_id="proj-1",
        context=PipelineContext(story_bible=StoryBible(title="Test", genre="Fantasy")),
    )
    prompt = stage._build_user_prompt(inp)
    assert "Test" in prompt
    assert "Fantasy" in prompt


def test_llm_stage_name():
    stage = LLMStage(name="planner", system_prompt="X", model="m")
    assert stage.name == "planner"
