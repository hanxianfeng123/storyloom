from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./storyloom.db"
    log_level: str = "INFO"
    pipeline_config_path: str = ""

    model_config = {"env_prefix": "STORYLOOM_", "env_file": ".env", "extra": "ignore"}
