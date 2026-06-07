from abc import ABC, abstractmethod

from storyloom.core.contract import StageInput, StageOutput, StageMetrics
from storyloom.providers import complete, estimate_cost


class Stage(ABC):
    name: str = ""

    @abstractmethod
    async def execute(self, input: StageInput) -> StageOutput:
        ...


class LLMStage(Stage):
    """Generic stage that builds a prompt and calls LiteLLM."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str,
        build_user_prompt=None,
        max_tokens: int = 4096,
        post_process=None,
    ):
        self.name = name
        self.model = model
        self._system_prompt = system_prompt
        self._build_user_prompt = build_user_prompt or self._default_user_prompt
        self._max_tokens = max_tokens
        self._post_process = post_process

    @staticmethod
    def _default_user_prompt(input: StageInput) -> str:
        ctx = input.context
        return (
            f"Title: {ctx.story_bible.title}\n"
            f"Genre: {ctx.story_bible.genre}\n"
            f"Previous chapters: {len(ctx.chapter_history)}\n"
            f"Style guide: {ctx.style_guide or 'None'}\n\n"
            f"Generate the next chapter."
        )

    def build_messages(self, input: StageInput) -> list[dict]:
        return [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": self._build_user_prompt(input)},
        ]

    async def execute(self, input: StageInput) -> StageOutput:
        messages = self.build_messages(input)
        response = await complete(messages, model=self.model, max_tokens=self._max_tokens)
        content = response.content
        if self._post_process:
            content = self._post_process(input, content)

        return StageOutput(
            content=content,
            decision="approved",
            metrics=StageMetrics(
                model=response.model,
                tokens_in=response.tokens_in,
                tokens_out=response.tokens_out,
                latency_ms=response.latency_ms,
                cost_usd=estimate_cost(response.model, response.tokens_in, response.tokens_out),
            ),
        )
