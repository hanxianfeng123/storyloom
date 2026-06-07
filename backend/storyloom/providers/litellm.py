"""LiteLLM-based provider that replaces all individual provider wrappers."""

import json
import time
from dataclasses import dataclass, field
from litellm import acompletion, cost_per_token, model_cost


@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_in: int
    tokens_out: int
    latency_ms: int


def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    try:
        prompt_cost, completion_cost = cost_per_token(
            model=model, prompt_tokens=tokens_in, completion_tokens=tokens_out
        )
        return round((prompt_cost or 0) + (completion_cost or 0), 6)
    except Exception:
        # Fallback: unknown model
        pricing = model_cost.get(model, {})
        if pricing:
            in_rate = pricing.get("input_cost_per_token", 3e-6)
            out_rate = pricing.get("output_cost_per_token", 15e-6)
        else:
            in_rate, out_rate = 3e-6, 15e-6
        return round(tokens_in * in_rate + tokens_out * out_rate, 6)


async def complete(
    messages: list[dict],
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> LLMResponse:
    """Unified LLM completion using LiteLLM. Accepts OpenAI-format messages."""
    start = time.monotonic()
    response = await acompletion(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    latency = int((time.monotonic() - start) * 1000)
    usage = getattr(response, "usage", None) or getattr(response, "_usage", None)
    tokens_in = usage.prompt_tokens if usage else 0
    tokens_out = usage.completion_tokens if usage else 0
    content = response.choices[0].message.content if response.choices else ""
    return LLMResponse(
        content=content or "",
        model=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency,
    )


@dataclass
class ToolCall:
    name: str
    arguments: dict = field(default_factory=dict)


async def complete_with_tools(
    messages: list[dict],
    model: str,
    tools: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> tuple[LLMResponse, list[ToolCall] | None]:
    """LLM completion with function calling support.

    Returns (llm_response, tool_calls_or_None).
    When the LLM returns text instead of calling a tool, tool_calls is None.
    """
    start = time.monotonic()
    response = await acompletion(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=temperature,
        max_tokens=max_tokens,
    )
    latency = int((time.monotonic() - start) * 1000)
    usage = getattr(response, "usage", None) or getattr(response, "_usage", None)
    tokens_in = usage.prompt_tokens if usage else 0
    tokens_out = usage.completion_tokens if usage else 0

    message = response.choices[0].message if response.choices else None
    content = message.content if message else ""
    tool_calls = None
    if message and message.tool_calls:
        tool_calls = []
        for tc in message.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except (json.JSONDecodeError, TypeError):
                args = {}
            tool_calls.append(ToolCall(name=tc.function.name, arguments=args))

    llm_resp = LLMResponse(
        content=content or "",
        model=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency,
    )
    return llm_resp, tool_calls
