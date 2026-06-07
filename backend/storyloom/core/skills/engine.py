"""Generic skill execution engine — renders templates, calls LiteLLM, logs runs."""

import uuid

from jinja2 import Template
from pydantic import BaseModel

from storyloom.core.contract import PipelineContext
from storyloom.core.skills.registry import SkillRegistry
from storyloom.memory.skill_store import SkillStore, SkillRun
from storyloom.providers import complete, estimate_cost


class SkillDef(BaseModel):
    """Runtime representation of a single skill, loaded from DB."""
    id: str
    category: str
    name: str
    description: str
    system_prompt: str
    user_prompt_template: str = ""
    post_process_template: str | None = None
    model: str
    fallback_model: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.7


class SkillOutput(BaseModel):
    """Result of a single skill execution."""
    content: str
    skill_name: str
    model_used: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    cost_usd: float


class SkillExecutionEngine:
    """Generic template-driven skill executor.

    Renders Jinja2 prompts, calls LiteLLM with the skill's model config,
    runs optional post-processing, logs the run to skill_runs.
    """

    def __init__(self, store: SkillStore, registry: SkillRegistry):
        self._store = store
        self._registry = registry
        self._step_counter = 0

    async def execute(
        self,
        skill_name: str,
        context: PipelineContext,
        rationale: str = "",
    ) -> SkillOutput:
        skill_dict = self._registry.get(skill_name)
        if not skill_dict:
            raise ValueError(f"Skill '{skill_name}' not found in registry")
        skill = SkillDef(**skill_dict)

        self._step_counter += 1

        # Render prompts
        messages = [
            {"role": "system", "content": skill.system_prompt},
            {"role": "user", "content": Template(skill.user_prompt_template).render(
                **context.model_dump(),
            )},
        ]

        # Call primary model
        response = await complete(
            messages=messages,
            model=skill.model,
            max_tokens=skill.max_tokens,
            temperature=skill.temperature,
        )

        content = response.content

        # Optional: try fallback on empty result
        if not content and skill.fallback_model:
            response = await complete(
                messages=messages,
                model=skill.fallback_model,
                max_tokens=skill.max_tokens,
                temperature=skill.temperature,
            )
            content = response.content

        # Post-process
        if skill.post_process_template and content:
            content = Template(skill.post_process_template).render(
                original_content=context.chapter_content or "",
                new_content=content,
            )

        cost = estimate_cost(response.model, response.tokens_in, response.tokens_out)

        # Persist run log
        run = SkillRun(
            id=uuid.uuid4().hex[:12],
            project_id=context.project_id,
            chapter_number=context.chapter_number,
            step_number=self._step_counter,
            skill_id=skill.id,
            llm_decision=rationale,
            input_preview=messages[-1].get("content", "")[:200],
            output_preview=content[:200] if content else "",
            tokens_in=response.tokens_in,
            tokens_out=response.tokens_out,
            latency_ms=response.latency_ms,
            cost_usd=cost,
            status="success" if content else "failed",
            error_message=None if content else "Empty response from LLM",
        )
        await self._store.log_run(run)

        return SkillOutput(
            content=content or "",
            skill_name=skill.name,
            model_used=response.model,
            tokens_in=response.tokens_in,
            tokens_out=response.tokens_out,
            latency_ms=response.latency_ms,
            cost_usd=cost,
        )
