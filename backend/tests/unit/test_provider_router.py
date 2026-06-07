from storyloom.providers.router import select


def test_select_returns_model_string():
    model = select("planner", "zh")
    assert isinstance(model, str)
    assert "claude" in model or "deepseek" in model


def test_select_writer_zh_uses_deepseek():
    model = select("writer", "zh")
    assert "deepseek" in model


def test_select_writer_en_uses_claude():
    model = select("writer", "en")
    assert "claude" in model


def test_select_unknown_stage_falls_back():
    model = select("unknown_stage", "zh")
    assert isinstance(model, str)
