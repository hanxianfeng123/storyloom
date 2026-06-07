from pydantic import BaseModel
from typing import Protocol


class Message(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMResponse(BaseModel):
    content: str
    model: str
    tokens_in: int
    tokens_out: int
    latency_ms: int


class LLMProvider(Protocol):
    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        ...
