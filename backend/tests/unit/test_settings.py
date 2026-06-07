from storyloom.config.settings import Settings


def test_defaults():
    s = Settings()
    assert s.database_url == "sqlite:///./storyloom.db"
    assert s.log_level == "INFO"
