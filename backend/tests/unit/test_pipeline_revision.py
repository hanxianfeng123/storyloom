import pytest
from storyloom.core.pipeline import PipelineOrchestrator
from storyloom.core.contract import StageInput, StageOutput, StageMetrics
from storyloom.core.stages.base import Stage


class RevisionStage(Stage):
    """Stage that always requests revision, up to a configurable number of calls."""

    name = "writer"
    call_count = 0

    async def execute(self, input: StageInput) -> StageOutput:
        RevisionStage.call_count += 1
        if RevisionStage.call_count <= 3:
            return StageOutput(
                content="needs revision",
                decision="need_revision",
                revise_target="writer",
                metrics=StageMetrics(model="t", tokens_in=0, tokens_out=0, latency_ms=0, cost_usd=0),
            )
        return StageOutput(
            content="finally approved",
            decision="approved",
            metrics=StageMetrics(model="t", tokens_in=0, tokens_out=0, latency_ms=0, cost_usd=0),
        )


@pytest.mark.asyncio
async def test_revision_loop_stops_after_max_retries():
    RevisionStage.call_count = 0
    stage = RevisionStage()
    orch = PipelineOrchestrator(stages=[stage])
    result = await orch.run("proj-1")
    assert result.status == "completed"
    # Should have forced pass after max revisions
    assert any(r["decision"] == "forced_pass" for r in result.stage_results)


@pytest.mark.asyncio
async def test_rejected_stage_fails_pipeline():
    class RejectStage(Stage):
        name = "quality_gate"
        async def execute(self, input: StageInput) -> StageOutput:
            return StageOutput(
                content="bad",
                decision="rejected",
                metrics=StageMetrics(model="t", tokens_in=0, tokens_out=0, latency_ms=0, cost_usd=0),
            )

    orch = PipelineOrchestrator(stages=[RejectStage()])
    result = await orch.run("proj-1")
    assert result.status == "failed"
