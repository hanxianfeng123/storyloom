import pytest
from storyloom.providers.router import ProviderRouter
from storyloom.providers.base import LLMProvider


def test_router_requires_provider_registration():
    router = ProviderRouter()
    assert len(router._providers) == 0


def test_register_provider():
    router = ProviderRouter()
    router.register("claude", "anthropic", MockProvider())
    assert "claude" in router._providers


def test_route_by_stage_and_language():
    router = ProviderRouter()
    mock = MockProvider()
    router.register("claude-sonnet", "anthropic", mock)
    router.register("deepseek-chat", "deepseek", mock)
    # Writer + zh -> DeepSeek
    model, provider = router.select("writer", "zh")
    assert model == "deepseek-chat"
    # Planner + en -> Claude
    model, provider = router.select("planner", "en")
    assert model == "claude-sonnet"


class MockProvider:
    async def complete(self, messages, model=None, temperature=0.7, max_tokens=4096):
        from storyloom.providers.base import LLMResponse
        return LLMResponse(content="mock", model=model or "mock", tokens_in=0, tokens_out=0, latency_ms=0)
