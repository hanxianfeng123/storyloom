import time
from anthropic import AsyncAnthropic
from storyloom.providers.base import LLMResponse, Message


class AnthropicProvider:
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        start = time.monotonic()
        system = ""
        chat_messages = []
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})
        response = await self.client.messages.create(
            model=model or "claude-sonnet-4-20250514",
            system=system or None,
            messages=chat_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency = int((time.monotonic() - start) * 1000)
        return LLMResponse(
            content=response.content[0].text if response.content else "",
            model=response.model,
            tokens_in=response.usage.input_tokens if response.usage else 0,
            tokens_out=response.usage.output_tokens if response.usage else 0,
            latency_ms=latency,
        )
