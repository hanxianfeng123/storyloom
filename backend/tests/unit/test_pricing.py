from storyloom.providers.pricing import estimate_cost


def test_claude_sonnet_pricing():
    cost = estimate_cost("claude-sonnet", tokens_in=1000, tokens_out=500)
    assert cost > 0
    assert cost < 1  # Should be < $1 for these token counts


def test_deepseek_pricing_cheaper():
    claude_cost = estimate_cost("claude-sonnet", tokens_in=1000, tokens_out=500)
    deepseek_cost = estimate_cost("deepseek-chat", tokens_in=1000, tokens_out=500)
    assert deepseek_cost < claude_cost


def test_unknown_model_defaults():
    cost = estimate_cost("unknown-model", tokens_in=1000, tokens_out=500)
    assert cost >= 0
