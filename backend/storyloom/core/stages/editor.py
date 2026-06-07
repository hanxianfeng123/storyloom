# DEPRECATED — will be removed in favor of DB-driven skills (definitions.yaml → editor).
from storyloom.core.stages.base import LLMStage
from storyloom.i18n.zh.prompts.editor import EDITOR_SYSTEM_PROMPT
from storyloom.providers.router import select


def build_editor_prompt(input):
    original = input.chapter_id or ""
    return (
        f"Edit this chapter. Preserve a change log at the end.\n\n"
        f"Draft:\n{original}"
    )


def editor_post_process(input, content: str) -> str:
    original = input.chapter_id or ""
    return content + (
        f"\n\n---\n## Editor Change Log\n"
        f"- Original length: {len(original)} chars\n"
        f"- Revised length: {len(content)} chars\n"
        f"- Changes: line edits, grammar fixes, style polish"
    )


EditorStage = LLMStage(
    name="editor",
    system_prompt=EDITOR_SYSTEM_PROMPT,
    model=select("editor", "zh"),
    build_user_prompt=build_editor_prompt,
    post_process=editor_post_process,
)
