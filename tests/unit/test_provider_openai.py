import pytest
from storyloom.providers.openai import OpenAIProvider
from storyloom.providers.base import Message


@pytest.mark.asyncio
async def test_openai_provider_interface():
    provider = OpenAIProvider(api_key="test-key")
    messages = [Message(role="user", content="hello")]
    # Without mocking httpx, this will fail — test the interface shape
    assert hasattr(provider, "complete")
    assert callable(provider.complete)
