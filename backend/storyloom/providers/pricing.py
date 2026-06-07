"""Per-model pricing in USD per 1M tokens."""

PRICING_TABLE = {
    # Anthropic
    "claude-sonnet-4":     {"input": 3.0,  "output": 15.0},
    "claude-sonnet":       {"input": 3.0,  "output": 15.0},
    "claude-3.5-sonnet":   {"input": 3.0,  "output": 15.0},
    "claude-3-haiku":      {"input": 0.25, "output": 1.25},
    # OpenAI
    "gpt-4o":              {"input": 2.5,  "output": 10.0},
    "gpt-4o-mini":         {"input": 0.15, "output": 0.6},
    # DeepSeek
    "deepseek-chat":       {"input": 0.14, "output": 0.28},
    # Default fallback
    "__default__":         {"input": 3.0,  "output": 15.0},
}


def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """Calculate estimated cost in USD for an LLM call."""
    pricing = PRICING_TABLE.get(model) or PRICING_TABLE["__default__"]
    cost = (tokens_in * pricing["input"] + tokens_out * pricing["output"]) / 1_000_000
    return round(cost, 6)
