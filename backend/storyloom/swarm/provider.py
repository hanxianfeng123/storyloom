"""backend/storyloom/swarm/provider.py"""
from __future__ import annotations
from abc import ABC, abstractmethod


class AgentProvider(ABC):
    """Interface for LLM-based agent execution.

    All provider implementations (Litellm, CAMEL, mock) must conform
    to this protocol.
    """

    @abstractmethod
    async def step(
        self,
        system_prompt: str,
        user_prompt: str,
        llm_config: dict | None = None,
    ) -> str:
        """Execute one agent step.

        Args:
            system_prompt: Agent's role definition and behavioral rules.
            user_prompt: Current context -- what the agent should respond to.
            llm_config: Optional model/temperature/token overrides.

        Returns:
            Agent's response text.
        """
        ...
