"""backend/storyloom/swarm/models.py"""
from __future__ import annotations
from enum import Enum
from typing import Any, Iterator, Literal
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    AGENT = "agent"
    GROUP = "group"
    POOL = "pool"


class AgentNode(BaseModel):
    """Tree node representing an agent, group, or pool.

    Tree only encodes organizational hierarchy and identity.
    No execution order, data flow, or error handling semantics.
    """
    id: str
    name: str
    node_type: NodeType = NodeType.AGENT
    parent_id: str | None = None
    children: list[AgentNode] = []

    # Agent identity (agent/pool only)
    system_prompt: str = ""
    llm_config: dict | None = None
    interests: list[str] = []

    # Pool config
    pool_size: int = 1

    def walk(self) -> Iterator[AgentNode]:
        """DFS walk yielding this node then all descendants."""
        yield self
        for child in self.children:
            yield from child.walk()

    def deep_copy(self) -> AgentNode:
        """Deep copy the entire subtree."""
        return self.model_copy(deep=True)

    def find(self, node_id: str) -> AgentNode | None:
        """Find a descendant by ID."""
        if self.id == node_id:
            return self
        for child in self.children:
            found = child.find(node_id)
            if found:
                return found
        return None


class Message(BaseModel):
    """Message sent between agents via the message bus."""
    from_id: str
    to_id: str | None = None          # None -> broadcast or group
    to_group: str | None = None       # Send to all nodes in this subtree
    msg_type: str
    payload: Any = None
    correlation_id: str | None = None  # For tracing conversation chains


class BlackboardEntry(BaseModel):
    """A single write to the blackboard, versioned."""
    key: str
    value: Any
    writer_id: str
    timestamp: float = 0.0
    version: int = 1


class RuntimeEvent(BaseModel):
    """Event emitted during runtime for observability."""
    event_type: Literal["node_start", "node_complete", "node_failed",
                        "llm_call", "message_sent", "blackboard_write",
                        "agent_decision"]
    node_id: str
    timestamp: float = 0.0
    data: dict = Field(default_factory=dict)


class NodeResult(BaseModel):
    """Result of a single agent execution cycle."""
    agent_id: str
    status: Literal["success", "skipped", "failed"] = "success"
    output_key: str | None = None
    output_value: Any = None
    token_usage: dict | None = None
