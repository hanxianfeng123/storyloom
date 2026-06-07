from storyloom.core.stages.base import Stage
from storyloom.core.contract import StageInput, StageOutput, StageMetrics
from storyloom.providers.base import LLMProvider, Message
from storyloom.providers.pricing import estimate_cost


class ContinuityStage(Stage):
    name = "continuity"

    def __init__(self, llm_provider: LLMProvider, model: str = "claude-sonnet"):
        self.provider = llm_provider
        self.model = model

    async def execute(self, input: StageInput) -> StageOutput:
        ctx = input.context
        recent = ctx.chapter_history[-3:] if ctx.chapter_history else []
        history_text = "\n".join(f"Ch {c.number}: {c.summary}" for c in recent)
        messages = [
            Message(role="system", content="You are a continuity checker. Compare the current chapter against the previous ones. List any discrepancies in character state, setting, objects, or plot threads. Be specific."),
            Message(role="user", content=f"Previous chapters:\n{history_text}\n\nCurrent chapter:\n{input.chapter_id or ''}\n\nList inconsistencies only."),
        ]
        response = await self.provider.complete(messages, model=self.model, max_tokens=1024)
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
