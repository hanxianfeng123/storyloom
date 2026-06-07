from pydantic import BaseModel, Field
from typing import Literal


class StoryBible(BaseModel):
    title: str
    genre: str
    summary: str = ""
    themes: list[str] = []


class CharacterCard(BaseModel):
    name: str
    role: str
    personality: str = ""
    appearance: str = ""
    background: str = ""


class WorldState(BaseModel):
    settings: dict[str, str] = {}


class ChapterSummary(BaseModel):
    number: int
    title: str
    word_count: int = 0
    summary: str = ""


class PipelineContext(BaseModel):
    story_bible: StoryBible
    character_cards: list[CharacterCard] = []
    world_state: WorldState = WorldState()
    chapter_history: list[ChapterSummary] = []
    style_guide: str | None = None


class StageMetrics(BaseModel):
    model: str
    tokens_in: int = Field(ge=0)
    tokens_out: int = Field(ge=0)
    latency_ms: int = Field(ge=0)
    cost_usd: float = Field(ge=0.0)


class StageInput(BaseModel):
    project_id: str
    chapter_id: str | None = None
    context: PipelineContext


class StageOutput(BaseModel):
    content: str | None = None
    partial: bool = False
    metrics: StageMetrics
    decision: Literal["approved", "rejected", "need_revision"]
    revise_target: Literal["writer", "editor"] | None = None
    revision_context: dict | None = None
    review_notes: str | None = None
