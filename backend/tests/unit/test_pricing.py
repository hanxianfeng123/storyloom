from storyloom.providers.litellm import estimate_cost


def test_estimate_cost_returns_number():
    cost = estimate_cost("anthropic/claude-sonnet-4-20250514", tokens_in=1000, tokens_out=500)
    assert cost > 0
    assert cost < 1


def test_cost_zero_with_zero_tokens():
    cost = estimate_cost("anthropic/claude-sonnet-4-20250514", tokens_in=0, tokens_out=0)
    assert cost == 0


def test_unknown_model_returns_fallback():
    cost = estimate_cost("unknown-model", tokens_in=1000, tokens_out=500)
    assert cost >= 0
