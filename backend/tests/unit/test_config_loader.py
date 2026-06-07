from storyloom.config.config_loader import load_pipeline_config


def test_load_default_config():
    config = load_pipeline_config()
    assert len(config.stages) == 5
    assert config.stages[0].name == "planner"
    assert config.review_gates.quality == "always"
    assert config.trust_mode.enabled is True
