from storyloom.core.stages.base import Stage
from storyloom.core.contract import StageInput, StageOutput, StageMetrics
from storyloom.providers.base import LLMProvider, Message
from storyloom.i18n.zh.prompts.writer import WRITER_SYSTEM_PROMPT
from storyloom.providers.pricing import estimate_cost


class WriterStage(Stage):
    name = "writer"

    def __init__(self, llm_provider: LLMProvider, model: str = "deepseek-chat"):
        self.provider = llm_provider
        self.model = model

    async def execute(self, input: StageInput) -> StageOutput:
        ctx = input.context
        outline = input.chapter_id or ""
        messages = [
            Message(role="system", content=WRITER_SYSTEM_PROMPT),
            Message(role="user", content=(
                f"Title: {ctx.story_bible.title}\n"
                f"Genre: {ctx.story_bible.genre}\n"
                f"Outline: {outline}\n"
                f"Style: {ctx.style_guide or 'Standard'}\n\n"
                f"Write the chapter."
            )),
        ]
        response = await self.provider.complete(messages, model=self.model)
        return StageOutput(
            content=response.content,
            decision="approved",
            metrics=StageMetrics(
                model=response.model,
                tokens_in=response.tokens_in,
                tokens_out=response.tokens_out,
                latency_ms=response.latency_ms,
                cost_usd=estimate_cost(response.model, response.tokens_in, response.tokens_out),
            ),
        )
