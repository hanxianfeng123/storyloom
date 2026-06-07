import pytest
from storyloom.providers.ollama import OllamaProvider
from storyloom.providers.base import Message


@pytest.mark.asyncio
async def test_ollama_provider_interface():
    provider = OllamaProvider()
    assert hasattr(provider, "complete")
    assert callable(provider.complete)
