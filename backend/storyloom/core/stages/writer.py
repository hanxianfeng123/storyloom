# DEPRECATED — will be removed in favor of DB-driven skills (definitions.yaml → writer).
from storyloom.core.stages.base import LLMStage
from storyloom.i18n.zh.prompts.writer import WRITER_SYSTEM_PROMPT
from storyloom.providers.router import select


def build_writer_prompt(input):
    ctx = input.context
    outline = input.chapter_id or ""
    return (
        f"Title: {ctx.story_bible.title}\n"
        f"Genre: {ctx.story_bible.genre}\n"
        f"Outline: {outline}\n"
        f"Style: {ctx.style_guide or 'Standard'}\n\n"
        f"Write the chapter."
    )


WriterStage = LLMStage(
    name="writer",
    system_prompt=WRITER_SYSTEM_PROMPT,
    model=select("writer", "zh"),
    build_user_prompt=build_writer_prompt,
)
