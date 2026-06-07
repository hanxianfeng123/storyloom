import pytest
from storyloom.providers.deepseek import DeepSeekProvider
from storyloom.providers.base import Message


@pytest.mark.asyncio
async def test_deepseek_provider_interface():
    provider = DeepSeekProvider(api_key="test-key")
    assert hasattr(provider, "complete")
    assert callable(provider.complete)
    assert str(provider.client.base_url) == "https://api.deepseek.com/v1/"
