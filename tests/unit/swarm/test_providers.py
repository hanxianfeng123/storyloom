"""tests/unit/swarm/test_providers.py"""
import pytest
from storyloom.swarm.provider import AgentProvider
from storyloom.swarm.providers.litellm_provider import LitellmProvider


class TestProviderContract:
    """Verify that AgentProvider protocol is properly defined."""

    def test_provider_has_step_method(self):
        """AgentProvider should define async step() with the right signature."""
        import inspect
        sig = inspect.signature(AgentProvider.step)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "system_prompt" in params
        assert "user_prompt" in params
        assert "llm_config" in params
        # Must be async (coroutine)
        assert inspect.iscoroutinefunction(AgentProvider.step)

    def test_provider_returns_string(self):
        """step() return annotation should be str."""
        import typing
        ret = typing.get_type_hints(AgentProvider.step).get("return")
        assert ret is str


@pytest.mark.asyncio
async def test_litellm_provider_interface():
    """LitellmProvider conforms to AgentProvider."""
    provider = LitellmProvider()
    assert isinstance(provider, AgentProvider)


@pytest.mark.asyncio
async def test_litellm_provider_calls_complete(monkeypatch):
    """Verify LitellmProvider delegates to complete() with correct args."""
    from storyloom.swarm.providers.litellm_provider import complete as mock_complete
    from storyloom.providers.litellm import LLMResponse

    call_args = {}

    async def fake_complete(messages, model, temperature, max_tokens):
        call_args["model"] = model
        call_args["temperature"] = temperature
        call_args["messages"] = messages
        return LLMResponse(content="mock reply", model=model,
                           tokens_in=10, tokens_out=5, latency_ms=100)

    monkeypatch.setattr("storyloom.swarm.providers.litellm_provider.complete", fake_complete)

    provider = LitellmProvider()
    result = await provider.step(
        system_prompt="You are a writer.",
        user_prompt="Write chapter 1",
        llm_config={"model": "deepseek/deepseek-chat", "temperature": 0.8},
    )
    assert result == "mock reply"
    assert call_args["model"] == "deepseek/deepseek-chat"
    assert call_args["temperature"] == 0.8


@pytest.mark.asyncio
async def test_litellm_provider_default_config(monkeypatch):
    """Default llm_config is used when none provided."""
    from storyloom.providers.litellm import LLMResponse

    async def fake_complete(messages, model, temperature, max_tokens):
        return LLMResponse(content="ok", model=model,
                           tokens_in=5, tokens_out=5, latency_ms=50)

    monkeypatch.setattr("storyloom.swarm.providers.litellm_provider.complete", fake_complete)
    provider = LitellmProvider(llm_config={"model": "default-model"})
    result = await provider.step("sys", "usr")
    assert result == "ok"
