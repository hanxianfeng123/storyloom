from pydantic import BaseModel
from datetime import datetime


class Skill(BaseModel):
    id: str
    category: str
    name: str
    parent_id: str | None = None
    description: str
    system_prompt: str
    user_prompt_template: str = ""
    post_process_template: str | None = None
    model: str = "anthropic/claude-sonnet-4-20250514"
    fallback_model: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.7
    version: int = 1
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SkillVersion(BaseModel):
    id: str
    skill_id: str
    version: int
    description: str
    system_prompt: str
    user_prompt_template: str = ""
    post_process_template: str | None = None
    model: str
    max_tokens: int
    temperature: float
    change_note: str = ""
    created_at: datetime | None = None
    created_by: str = "system"


class SkillRun(BaseModel):
    id: str
    project_id: str
    chapter_number: int
    step_number: int
    skill_id: str
    llm_decision: str | None = None
    input_preview: str | None = None
    output_preview: str | None = None
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0
    status: str = "success"
    error_message: str | None = None
    created_at: datetime | None = None


class SkillUpdate(BaseModel):
    description: str | None = None
    system_prompt: str | None = None
    user_prompt_template: str | None = None
    post_process_template: str | None = None
    model: str | None = None
    fallback_model: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    is_active: bool | None = None
    change_note: str = ""
