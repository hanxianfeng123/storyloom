"""Provider base was replaced by LiteLLM — LLMResponse lives in providers.litellm now."""
from storyloom.providers.litellm import LLMResponse


def test_llm_response_creation():
    resp = LLMResponse(content="Hello", model="claude-3", tokens_in=10, tokens_out=5, latency_ms=100)
    assert resp.content == "Hello"
    assert resp.model == "claude-3"
