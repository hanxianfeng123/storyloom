# DEPRECATED — will be removed in favor of DB-driven skills (definitions.yaml → continuity).
from storyloom.core.stages.base import LLMStage
from storyloom.providers.router import select


def build_continuity_prompt(input):
    ctx = input.context
    recent = ctx.chapter_history[-3:] if ctx.chapter_history else []
    history_text = "\n".join(f"Ch {c.number}: {c.summary}" for c in recent)
    return (
        f"Previous chapters:\n{history_text}\n\n"
        f"Current chapter:\n{input.chapter_id or ''}\n\n"
        f"List inconsistencies only."
    )


CONTINUITY_SYSTEM_PROMPT = (
    "You are a continuity checker. Compare the current chapter against "
    "the previous ones. List any discrepancies in character state, setting, "
    "objects, or plot threads. Be specific."
)

ContinuityStage = LLMStage(
    name="continuity",
    system_prompt=CONTINUITY_SYSTEM_PROMPT,
    model=select("continuity", "zh"),
    build_user_prompt=build_continuity_prompt,
    max_tokens=1024,
)
