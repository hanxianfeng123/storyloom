import pytest
from pydantic import ValidationError
from storyloom.core.contract import (
    StageOutput,
    PipelineContext,
    StageMetrics,
    StoryBible,
    CharacterCard,
    WorldState,
    ChapterSummary,
)


def test_stage_metrics_requires_positive_tokens():
    with pytest.raises(ValidationError):
        StageMetrics(model="test", tokens_in=-1, tokens_out=100, latency_ms=100, cost_usd=0)


def test_stage_output_valid_decision():
    output = StageOutput(
        content="chapter text",
        decision="approved",
        metrics=StageMetrics(model="claude", tokens_in=100, tokens_out=200, latency_ms=500, cost_usd=0.01),
    )
    assert output.decision == "approved"


def test_stage_output_need_revision_requires_target():
    output = StageOutput(
        content="text",
        decision="need_revision",
        revise_target="writer",
        revision_context={"issue": "plot hole"},
        metrics=StageMetrics(model="claude", tokens_in=100, tokens_out=200, latency_ms=500, cost_usd=0.01),
    )
    assert output.revise_target == "writer"


def test_pipeline_context_construction():
    ctx = PipelineContext(
        story_bible=StoryBible(title="Test Novel", genre="Fantasy"),
        character_cards=[CharacterCard(name="Alice", role="protagonist")],
        world_state=WorldState(settings={"season": "autumn"}),
        chapter_history=[ChapterSummary(number=1, title="Ch1", word_count=2000)],
    )
    assert ctx.story_bible.title == "Test Novel"
    assert len(ctx.character_cards) == 1
