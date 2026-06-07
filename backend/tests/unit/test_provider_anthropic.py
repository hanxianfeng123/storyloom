import pytest
from storyloom.providers.anthropic import AnthropicProvider
from storyloom.providers.base import Message


@pytest.mark.asyncio
async def test_anthropic_provider_interface():
    provider = AnthropicProvider(api_key="test-key")
    assert hasattr(provider, "complete")
    assert callable(provider.complete)
