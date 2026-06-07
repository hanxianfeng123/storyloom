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


class SkillRunLog(BaseModel):
    """A single entry in the execution log, appended after each skill run."""
    step: int
    skill_name: str
    rationale: str = ""
    content_preview: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    status: str = "success"


class SupervisorConfig(BaseModel):
    max_steps: int = 20
    max_cost_usd: float = 0.50
    model: str = "anthropic/claude-sonnet-4-20250514"
    temperature: float = 0.3
    max_tokens: int = 1024


class SupervisorResult(BaseModel):
    pipeline_id: str
    status: str  # completed | partial | failed
    chapter_content: str | None = None
    current_outline: str | None = None
    skill_log: list[SkillRunLog] = []
    total_steps: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    summary: str = ""


class PipelineContext(BaseModel):
    project_id: str = ""
    chapter_number: int = 0
    story_bible: StoryBible
    character_cards: list[CharacterCard] = []
    world_state: WorldState = WorldState()
    chapter_history: list[ChapterSummary] = []
    style_guide: str | None = None
    revision_hint: dict | None = None
    # Layer 2: Accumulating (current chapter)
    chapter_content: str | None = None
    current_outline: str | None = None
    quality_report: dict | None = None
    # Layer 3: Ephemeral (single skill execution)
    supervisor_instructions: str | None = None
    revision_focus: list[str] | None = None
    # Execution log
    skill_log: list[SkillRunLog] = []


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
