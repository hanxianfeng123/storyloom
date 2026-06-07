from pydantic_settings import BaseSettings
from pydantic import Field, model_validator


class Settings(BaseSettings):
    database_url: str = "sqlite:///./storyloom.db"
    log_level: str = "INFO"
    llm_providers: dict = {}
    pipeline_config_path: str = ""

    model_config = {"env_prefix": "STORYLOOM_"}

    @model_validator(mode="after")
    def validate_llm_providers(self) -> "Settings":
        for provider, config in self.llm_providers.items():
            if provider == "openai" and "api_key" not in config:
                from pydantic import ValidationError

                raise ValidationError.from_exception_data(
                    "Settings",
                    [
                        {
                            "type": "missing",
                            "loc": ("llm_providers", provider, "api_key"),
                            "msg": f"Field required for provider '{provider}'",
                            "input": config,
                        }
                    ],
                )
        return self
