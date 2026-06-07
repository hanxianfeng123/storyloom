from storyloom.providers.base import LLMProvider

DEFAULT_ROUTING = {
    ("planner", "zh"): "claude-sonnet",
    ("planner", "en"): "claude-sonnet",
    ("writer", "zh"): "deepseek-chat",
    ("writer", "en"): "claude-sonnet",
    ("editor", "zh"): "claude-sonnet",
    ("editor", "en"): "claude-sonnet",
    ("quality", "zh"): "claude-sonnet",
    ("quality", "en"): "claude-sonnet",
    ("continuity", "zh"): "claude-sonnet",
    ("continuity", "en"): "claude-sonnet",
}


class ProviderRouter:
    def __init__(self) -> None:
        self._providers: dict[str, tuple[str, LLMProvider]] = {}
        self._routing: dict[tuple[str, str], str] = dict(DEFAULT_ROUTING)

    def register(self, model_name: str, provider_type: str, provider: LLMProvider) -> None:
        self._providers[model_name] = (provider_type, provider)

    def select(self, stage: str, language: str = "zh") -> tuple[str, LLMProvider | None]:
        model_name = self._routing.get((stage, language), "claude-sonnet")
        _, provider = self._providers.get(model_name, (None, None))
        return model_name, provider

    def override_routing(self, stage: str, language: str, model_name: str) -> None:
        self._routing[(stage, language)] = model_name
