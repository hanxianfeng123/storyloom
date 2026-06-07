import pytest
from unittest.mock import patch, AsyncMock
from storyloom.core.stages.quality_gate import QualityGateStage


@pytest.mark.asyncio
async def test_llm_review_returns_all_5_dimensions():
    mock_response = AsyncMock()
    mock_response.content = (
        '{"plot_consistency": {"score": "pass", "reason": "ok"}, '
        '"character_voice": {"score": "flag", "reason": "slight inconsistency"}, '
        '"prose_quality": {"score": "pass", "reason": "good"}, '
        '"pacing": {"score": "pass", "reason": "fine"}, '
        '"language_accuracy": {"score": "pass", "reason": "ok"}}'
    )
    mock_response.model = "mock"
    mock_response.tokens_in = 50
    mock_response.tokens_out = 20
    mock_response.latency_ms = 100

    with patch("storyloom.providers.litellm.complete", new_callable=AsyncMock, return_value=mock_response):
        gate = QualityGateStage(model="mock-model")
        result = await gate._llm_review("chapter text", "en")
        assert "plot_consistency" in result
        assert "character_voice" in result
        assert "prose_quality" in result
        assert "pacing" in result
        assert "language_accuracy" in result
