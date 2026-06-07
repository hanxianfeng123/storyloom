from storyloom.core.errors import LLMError, StageError, ProviderError


def test_llm_error_is_exception():
    err = LLMError("API error", model="claude-3")
    assert isinstance(err, Exception)
    assert str(err) == "API error"
    assert err.model == "claude-3"


def test_stage_error_has_stage_name():
    err = StageError("Writer failed", stage="writer")
    assert err.stage == "writer"


def test_provider_error_is_llm_error():
    err = ProviderError("Rate limited", provider="openai", status_code=429)
    assert isinstance(err, LLMError)
    assert err.status_code == 429
