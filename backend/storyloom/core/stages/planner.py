# DEPRECATED — will be removed in favor of DB-driven skills (definitions.yaml → planner).
from storyloom.core.stages.base import LLMStage
from storyloom.i18n.zh.prompts.planner import PLANNER_SYSTEM_PROMPT
from storyloom.providers.router import select


def build_planner_prompt(input):
    ctx = input.context
    return (
        f"Title: {ctx.story_bible.title}\n"
        f"Genre: {ctx.story_bible.genre}\n"
        f"Summary: {ctx.story_bible.summary}\n"
        f"Previous chapters: {len(ctx.chapter_history)}\n"
        f"Style guide: {ctx.style_guide or 'None'}\n\n"
        f"Generate an outline for the next chapter."
    )


PlannerStage = LLMStage(
    name="planner",
    system_prompt=PLANNER_SYSTEM_PROMPT,
    model=select("planner", "zh"),
    build_user_prompt=build_planner_prompt,
)
