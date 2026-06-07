import yaml
from pathlib import Path
from pydantic import BaseModel


class StageConfig(BaseModel):
    name: str
    model_ref: str
    provider: str


class ReviewGateConfig(BaseModel):
    planner: str = "optional"
    writer: str = "skip"
    editor: str = "optional"
    continuity: str = "skip"
    quality: str = "always"


class TrustModeConfig(BaseModel):
    enabled: bool = True
    auto_approve_after: int = 5


class PipelineConfig(BaseModel):
    stages: list[StageConfig]
    review_gates: ReviewGateConfig = ReviewGateConfig()
    trust_mode: TrustModeConfig = TrustModeConfig()


def load_pipeline_config(path: str | None = None) -> PipelineConfig:
    if path is None:
        path = str(Path(__file__).parent / "pipeline.yaml")
    with open(path) as f:
        data = yaml.safe_load(f)
    return PipelineConfig(**data)
