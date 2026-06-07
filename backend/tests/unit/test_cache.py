import pytest
from storyloom.core.cache import LLMCache
from storyloom.providers.litellm import LLMResponse


@pytest.mark.asyncio
async def test_cache_hit():
    cache = LLMCache()
    key = cache.make_key("gpt-4", [{"role": "user", "content": "hello"}])
    # put expects a dict-like key and LLMResponse value
    cache.put(key, LLMResponse(content="hi", model="gpt-4", tokens_in=10, tokens_out=5, latency_ms=100))
    hit = cache.get(key)
    assert hit is not None
    assert hit.content == "hi"


@pytest.mark.asyncio
async def test_cache_miss():
    cache = LLMCache()
    hit = cache.get("nonexistent")
    assert hit is None


@pytest.mark.asyncio
async def test_cache_max_size():
    cache = LLMCache(max_size=2)
    cache.put("k1", LLMResponse(content="a", model="m", tokens_in=1, tokens_out=1, latency_ms=1))
    cache.put("k2", LLMResponse(content="b", model="m", tokens_in=1, tokens_out=1, latency_ms=1))
    cache.put("k3", LLMResponse(content="c", model="m", tokens_in=1, tokens_out=1, latency_ms=1))
    assert cache.get("k1") is None  # evicted
    assert cache.get("k3") is not None
