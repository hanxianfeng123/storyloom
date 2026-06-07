import pytest
from storyloom.core.pipeline import PipelineOrchestrator
from storyloom.core.contract import StageInput, StageOutput, StageMetrics, PipelineContext, StoryBible
from storyloom.core.stages.base import Stage


class PassStage(Stage):
    name = "pass_stage"
    async def execute(self, input: StageInput) -> StageOutput:
        return StageOutput(
            content="passed",
            decision="approved",
            metrics=StageMetrics(model="t", tokens_in=0, tokens_out=0, latency_ms=0, cost_usd=0),
        )


@pytest.mark.asyncio
async def test_orchestrator_runs_all_stages():
    stage_a = PassStage()
    stage_b = PassStage()
    orch = PipelineOrchestrator(stages=[stage_a, stage_b])
    result = await orch.run("proj-1")
    assert result.status == "completed"
    assert len(result.stage_results) == 2


@pytest.mark.asyncio
async def test_orchestrator_cancellation():
    stage = PassStage()
    orch = PipelineOrchestrator(stages=[stage, stage])
    await orch.cancel()
    result = await orch.run("proj-1")
    assert result.status == "cancelled"
