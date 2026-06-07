import pytest
from pydantic import ValidationError
from storyloom.config.settings import Settings


def test_defaults():
    s = Settings()
    assert s.database_url == "sqlite:///./storyloom.db"
    assert s.log_level == "INFO"


def test_openai_key_required_for_openai_provider():
    with pytest.raises(ValidationError):
        Settings(llm_providers={"openai": {}})


def test_default_providers_empty():
    s = Settings()
    assert s.llm_providers == {}
