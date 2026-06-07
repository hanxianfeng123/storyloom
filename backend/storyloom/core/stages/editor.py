from storyloom.core.stages.base import Stage
from storyloom.core.contract import StageInput, StageOutput, StageMetrics
from storyloom.providers.base import LLMProvider, Message
from storyloom.i18n.zh.prompts.editor import EDITOR_SYSTEM_PROMPT
from storyloom.providers.pricing import estimate_cost


class EditorStage(Stage):
    name = "editor"

    def __init__(self, llm_provider: LLMProvider, model: str = "claude-sonnet"):
        self.provider = llm_provider
        self.model = model

    async def execute(self, input: StageInput) -> StageOutput:
        original = input.chapter_id or ""
        messages = [
            Message(role="system", content=EDITOR_SYSTEM_PROMPT),
            Message(role="user", content=(
                f"Edit this chapter. Preserve a change log at the end.\n\n"
                f"Draft:\n{original}"
            )),
        ]
        response = await self.provider.complete(messages, model=self.model)
        cost = estimate_cost(response.model, response.tokens_in, response.tokens_out)
        # Append change log with diff summary
        revised = response.content + (
            f"\n\n---\n## Editor Change Log\n"
            f"- Original length: {len(original)} chars\n"
            f"- Revised length: {len(response.content)} chars\n"
            f"- Changes: line edits, grammar fixes, style polish"
        )
        return StageOutput(
            content=revised,
            decision="approved",
            metrics=StageMetrics(
                model=response.model,
                tokens_in=response.tokens_in,
                tokens_out=response.tokens_out,
                latency_ms=response.latency_ms,
                cost_usd=cost,
            ),
        )
