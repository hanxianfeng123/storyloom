"""LLM-driven supervisor that orchestrates chapter generation via function calling."""

import uuid
from collections import Counter

from storyloom.core.contract import (
    PipelineContext,
    SkillRunLog,
    SupervisorConfig,
    SupervisorResult,
)
from storyloom.core.skills.engine import SkillExecutionEngine
from storyloom.core.skills.registry import SkillRegistry
from storyloom.memory.skill_store import SkillStore
from storyloom.providers import complete_with_tools

CHAPTER_COMPLETE_TOOL = {
    "type": "function",
    "function": {
        "name": "chapter_complete",
        "description": "Signal that the chapter is complete and the pipeline should stop.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Brief summary of what was accomplished this session.",
                },
            },
            "required": ["summary"],
        },
    },
}

SUPERVISOR_SYSTEM_PROMPT = (
    "You are the writing supervisor for a novel generation pipeline. "
    "Your job is to orchestrate chapter creation by delegating to specialist skills. "
    "Think of yourself as an editor-in-chief coordinating your team.\n\n"
    "## Decision Process\n"
    "Each turn, review the current state and call ONE of the available skills. "
    "After the skill executes, the result will be added to the context. "
    "Repeat until the chapter is complete.\n\n"
    "## Completion Criteria\n"
    "Call chapter_complete only when ALL of these are satisfied:\n"
    "1. Full chapter content exists (at least 500 characters)\n"
    "2. Prose has been edited for quality\n"
    "3. No continuity issues remain\n"
    "4. Quality assessment passes all dimensions\n\n"
    "## Rules\n"
    "- Start with planner if there's no outline yet\n"
    "- Always call exactly one skill per turn\n"
    "- Provide a brief rationale with each skill call explaining why you chose it\n"
    "- If a skill fails or returns nothing useful, try a different approach"
)


class SupervisorPipeline:
    """LLM-driven decision loop that selects and executes skills autonomously."""

    def __init__(
        self,
        engine: SkillExecutionEngine,
        registry: SkillRegistry,
        store: SkillStore,
        config: SupervisorConfig | None = None,
    ):
        self._engine = engine
        self._registry = registry
        self._store = store
        self._config = config or SupervisorConfig()

    def _build_tools(self) -> list[dict]:
        tools = []
        for skill in self._registry.list_active():
            tools.append({
                "type": "function",
                "function": {
                    "name": skill["name"],
                    "description": skill["description"],
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "rationale": {
                                "type": "string",
                                "description": "Why this skill is needed right now.",
                            },
                            "instructions": {
                                "type": "string",
                                "description": "Specific guidance or focus for this call.",
                            },
                        },
                        "required": ["rationale"],
                    },
                },
            })
        tools.append(CHAPTER_COMPLETE_TOOL)
        return tools

    def _build_state_summary(self, ctx: PipelineContext) -> str:
        lines = []
        has_content = ctx.chapter_content is not None and len(ctx.chapter_content) > 50
        lines.append("## Current State")
        lines.append(f"- Chapter: {ctx.chapter_number}")
        if has_content:
            lines.append(f"- Draft: {len(ctx.chapter_content)} chars")
        else:
            lines.append("- Draft: Not started")
        lines.append(f"- Outline: {'Yes' if ctx.current_outline else 'No'}")
        if ctx.skill_log:
            recent = ctx.skill_log[-5:]
            lines.append(
                f"\n## Recent Activity (last {len(recent)} steps)"
            )
            for entry in recent:
                mark = "✓" if entry.status == "success" else "✗"
                lines.append(
                    f"  Step {entry.step}: {mark} {entry.skill_name}"
                    f" ({entry.tokens_used} tokens)"
                )
        if ctx.supervisor_instructions:
            lines.append(f"\n## Instructions\n{ctx.supervisor_instructions}")
        return "\n".join(lines)

    async def _load_historical_patterns(
        self, project_id: str, chapter_number: int
    ) -> str:
        if not project_id:
            return ""
        runs = await self._store.list_runs(project_id)
        if not runs:
            return ""

        skill_counts: Counter = Counter()
        token_sums: dict[str, int] = {}
        for r in runs:
            name = r.llm_decision or "unknown"
            skill_counts[name] += 1
            token_sums[name] = token_sums.get(name, 0) + r.tokens_in + r.tokens_out

        lines = ["## Historical Skill Usage"]
        for name, count in skill_counts.most_common():
            avg = token_sums[name] // count
            lines.append(f"  - {name}: used {count}x, avg {avg} tokens")

        prev = [r for r in runs if r.chapter_number == chapter_number - 1]
        if prev:
            steps = " → ".join(r.skill_id[:8] for r in sorted(prev, key=lambda x: x.step_number))
            lines.append(f"\n## Previous Chapter Pattern\n  Ch {chapter_number - 1}: {steps}")

        return "\n".join(lines)

    async def run(
        self,
        context: PipelineContext,
        pipeline_id: str | None = None,
    ) -> SupervisorResult:
        pid = pipeline_id or uuid.uuid4().hex[:12]
        total_tokens = 0
        total_cost = 0.0
        same_skill_streak = 0
        prev_skill = ""
        summary = ""
        chapter_complete_called = False

        historical = ""
        if context.project_id:
            historical = await self._load_historical_patterns(
                context.project_id, context.chapter_number
            )

        tools = self._build_tools()
        system_content = SUPERVISOR_SYSTEM_PROMPT
        if historical:
            system_content += "\n\n" + historical

        for step in range(self._config.max_steps):
            state = self._build_state_summary(context)
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": state},
            ]

            if same_skill_streak >= 3:
                messages.append({
                    "role": "user",
                    "content": (
                        "Warning: you have called the same skill multiple times "
                        "in a row. Try a different approach."
                    ),
                })

            resp, tool_calls = await complete_with_tools(
                messages=messages,
                model=self._config.model,
                tools=tools,
                temperature=self._config.temperature,
                max_tokens=self._config.max_tokens,
            )

            total_tokens += resp.tokens_in + resp.tokens_out

            if not tool_calls:
                context.supervisor_instructions = (
                    "You must call exactly one skill per turn. Pick a skill."
                )
                continue

            tc = tool_calls[0]
            if tc.name == "chapter_complete":
                summary = tc.arguments.get("summary", "")
                chapter_complete_called = True
                break

            # Repeated-skill detection
            if tc.name == prev_skill:
                same_skill_streak += 1
            else:
                same_skill_streak = 0
                prev_skill = tc.name

            instructions = tc.arguments.get("instructions", "")
            context.supervisor_instructions = instructions or None

            try:
                output = await self._engine.execute(
                    tc.name, context, rationale=tc.arguments.get("rationale", "")
                )
            except ValueError:
                context.supervisor_instructions = (
                    f"Skill '{tc.name}' not found. Pick a different one."
                )
                continue

            total_cost += output.cost_usd

            # Update context based on skill type
            if tc.name in ("writer", "editor"):
                context.chapter_content = output.content
            elif tc.name == "planner":
                context.current_outline = output.content
            elif tc.name == "quality":
                context.quality_report = {"result": output.content}

            context.skill_log.append(SkillRunLog(
                step=step + 1,
                skill_name=tc.name,
                rationale=tc.arguments.get("rationale", ""),
                content_preview=output.content[:120],
                tokens_used=output.tokens_in + output.tokens_out,
                cost_usd=output.cost_usd,
                status="success",
            ))

            # Cost guardrail
            if total_cost > self._config.max_cost_usd:
                summary = "Cost limit reached."
                chapter_complete_called = True
                break

        status = "completed" if chapter_complete_called else "partial"
        return SupervisorResult(
            pipeline_id=pid,
            status=status,
            chapter_content=context.chapter_content,
            current_outline=context.current_outline,
            skill_log=context.skill_log,
            total_steps=len(context.skill_log),
            total_tokens=total_tokens,
            total_cost_usd=round(total_cost, 6),
            summary=summary,
        )
