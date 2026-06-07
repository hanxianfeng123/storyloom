import pytest
from unittest.mock import patch, AsyncMock
from storyloom.providers.litellm import complete, LLMResponse


@pytest.mark.asyncio
async def test_complete_returns_llm_response():
    """Verify the `complete` function returns a properly structured LLMResponse."""
    mock_acompletion = AsyncMock()
    mock_acompletion.choices = [
        type("Choice", (), {"message": type("Msg", (), {"content": "Hello world"})})()
    ]
    mock_acompletion.usage = type("Usage", (), {"prompt_tokens": 10, "completion_tokens": 5})()

    with patch("storyloom.providers.litellm.acompletion", return_value=mock_acompletion):
        result = await complete(
            messages=[{"role": "user", "content": "hi"}],
            model="test-model",
        )
    assert isinstance(result, LLMResponse)
    assert result.content == "Hello world"
    assert result.model == "test-model"
    assert result.tokens_in == 10
    assert result.tokens_out == 5
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_complete_empty_content():
    """Handle empty response content gracefully."""
    mock_acompletion = AsyncMock()
    mock_acompletion.choices = [
        type("Choice", (), {"message": type("Msg", (), {"content": None})})()
    ]
    mock_acompletion.usage = type("Usage", (), {"prompt_tokens": 0, "completion_tokens": 0})()

    with patch("storyloom.providers.litellm.acompletion", return_value=mock_acompletion):
        result = await complete(
            messages=[{"role": "user", "content": "hi"}],
            model="test-model",
        )
    assert result.content == ""
    assert result.tokens_in == 0
