import pytest
from storyloom.core.stages.quality_gate import QualityGateStage


class MockReviewProvider:
    async def complete(self, messages, **kwargs):
        from storyloom.providers.base import LLMResponse
        return LLMResponse(
            content='{"plot_consistency": {"score": "pass", "reason": "ok"}, "character_voice": {"score": "flag", "reason": "slight inconsistency"}, "prose_quality": {"score": "pass", "reason": "good"}, "pacing": {"score": "pass", "reason": "fine"}, "language_accuracy": {"score": "pass", "reason": "ok"}}',
            model="mock", tokens_in=50, tokens_out=20, latency_ms=100,
        )


@pytest.mark.asyncio
async def test_llm_review_returns_all_5_dimensions():
    gate = QualityGateStage(llm_provider=MockReviewProvider())
    result = await gate._llm_review("chapter text", "en")
    assert "plot_consistency" in result
    assert "character_voice" in result
    assert "prose_quality" in result
    assert "pacing" in result
    assert "language_accuracy" in result


@pytest.mark.asyncio
async def test_llm_review_parses_json():
    gate = QualityGateStage(llm_provider=MockReviewProvider())
    result = await gate._llm_review("chapter text", "en")
    assert isinstance(result["plot_consistency"], dict)
    assert "score" in result["plot_consistency"]
    assert "reason" in result["plot_consistency"]
