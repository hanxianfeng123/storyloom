"""backend/storyloom/swarm/providers/litellm_provider.py"""
from storyloom.swarm.provider import AgentProvider
from storyloom.providers.litellm import complete


class LitellmProvider(AgentProvider):
    """AgentProvider implementation using LiteLLM."""

    def __init__(self, llm_config: dict | None = None):
        self._default_config = llm_config or {}

    async def step(
        self,
        system_prompt: str,
        user_prompt: str,
        llm_config: dict | None = None,
    ) -> str:
        cfg = {**self._default_config, **(llm_config or {})}
        model = cfg.get("model", "deepseek/deepseek-chat")
        temperature = cfg.get("temperature", 0.7)
        max_tokens = cfg.get("max_tokens", 4096)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        resp = await complete(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.content
