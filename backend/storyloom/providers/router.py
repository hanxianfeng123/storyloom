"""Provider router — maps (stage, language) to a LiteLLM model string."""

DEFAULT_ROUTING = {
    ("planner", "zh"): "anthropic/claude-sonnet-4-20250514",
    ("planner", "en"): "anthropic/claude-sonnet-4-20250514",
    ("writer", "zh"): "deepseek/deepseek-chat",
    ("writer", "en"): "anthropic/claude-sonnet-4-20250514",
    ("editor", "zh"): "anthropic/claude-sonnet-4-20250514",
    ("editor", "en"): "anthropic/claude-sonnet-4-20250514",
    ("quality", "zh"): "anthropic/claude-sonnet-4-20250514",
    ("quality", "en"): "anthropic/claude-sonnet-4-20250514",
    ("continuity", "zh"): "anthropic/claude-sonnet-4-20250514",
    ("continuity", "en"): "anthropic/claude-sonnet-4-20250514",
}


def select(stage: str, language: str = "zh") -> str:
    return DEFAULT_ROUTING.get((stage, language), "anthropic/claude-sonnet-4-20250514")
