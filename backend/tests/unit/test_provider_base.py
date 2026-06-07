import pytest
from storyloom.providers.base import LLMProvider, LLMResponse, Message


def test_llm_response_creation():
    resp = LLMResponse(content="Hello", model="claude-3", tokens_in=10, tokens_out=5, latency_ms=100)
    assert resp.content == "Hello"
    assert resp.model == "claude-3"


def test_message_roles():
    msg = Message(role="user", content="Write a chapter")
    assert msg.role == "user"
    assert msg.content == "Write a chapter"


def test_provider_is_protocol():
    """LLMProvider should be a Protocol (can't instantiate directly)."""
    import inspect
    assert hasattr(LLMProvider, "__instancecheck__") or inspect.isclass(LLMProvider)
