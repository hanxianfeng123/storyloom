"""tests/unit/swarm/test_runtime.py"""
import asyncio

import pytest
from storyloom.swarm.models import AgentNode
from storyloom.swarm.blackboard import InMemoryBlackboard
from storyloom.swarm.message_bus import InMemoryMessageBus
from storyloom.swarm.provider import AgentProvider
from storyloom.swarm.runtime import SwarmRuntime, AgentContext


class MockProvider(AgentProvider):
    """Provider that records calls and returns canned responses."""

    def __init__(self, response: str = "mock output"):
        self.response = response
        self.calls = []

    async def step(self, system_prompt: str, user_prompt: str, llm_config=None) -> str:
        self.calls.append({"system": system_prompt, "user": user_prompt, "config": llm_config})
        return self.response


@pytest.mark.asyncio
async def test_runtime_starts_agent_loop():
    """Runtime starts one asyncio.Task per agent node."""
    agent = AgentNode(id="test-agent", name="Test", node_type="agent")
    runtime = SwarmRuntime(
        tree=agent,
        blackboard=InMemoryBlackboard(),
        bus=InMemoryMessageBus(),
        provider=MockProvider(),
    )
    await runtime.start()
    assert "test-agent" in runtime._tasks
    assert runtime._tasks["test-agent"] is not None
    assert not runtime._tasks["test-agent"].done()
    await runtime.stop()


@pytest.mark.asyncio
async def test_runtime_starts_group_children():
    """Runtime starts tasks for all agents in a group."""
    leaf = AgentNode(id="leaf", name="Leaf", node_type="agent")
    group = AgentNode(id="group", name="Group", node_type="group", children=[leaf])
    runtime = SwarmRuntime(
        tree=group,
        blackboard=InMemoryBlackboard(),
        bus=InMemoryMessageBus(),
        provider=MockProvider(),
    )
    await runtime.start()
    assert "leaf" in runtime._tasks
    await runtime.stop()


@pytest.mark.asyncio
async def test_runtime_starts_pool_instances():
    """Runtime starts pool_size tasks for a pool node."""
    pool = AgentNode(id="writers", name="Writers", node_type="pool", pool_size=3)
    runtime = SwarmRuntime(
        tree=pool,
        blackboard=InMemoryBlackboard(),
        bus=InMemoryMessageBus(),
        provider=MockProvider(),
    )
    await runtime.start()
    assert "writers.0" in runtime._tasks
    assert "writers.1" in runtime._tasks
    assert "writers.2" in runtime._tasks
    await runtime.stop()


@pytest.mark.asyncio
async def test_agent_reacts_to_blackboard_change():
    """Agent runs a cycle when a subscribed blackboard key changes."""
    provider = MockProvider(response="I see the update")
    agent = AgentNode(
        id="watcher", name="Watcher", node_type="agent",
        system_prompt="You watch things.",
        interests=["signal.*"],
    )
    bb = InMemoryBlackboard()
    bus = InMemoryMessageBus()
    runtime = SwarmRuntime(tree=agent, blackboard=bb, bus=bus, provider=provider)

    await runtime.start()
    await asyncio.sleep(0.05)

    # Write something the agent is watching
    await bb.write("signal.start", "go", "chief")
    # Wait longer than the agent's idle sleep (0.5s) so it detects the change
    await asyncio.sleep(0.6)

    # Agent should have called its provider
    assert len(provider.calls) > 0
    assert "You watch things." in provider.calls[0]["system"]
    await runtime.stop()


@pytest.mark.asyncio
async def test_agent_ignores_unwatched_keys():
    """Agent does NOT run when an uninterested key changes."""
    provider = MockProvider()
    agent = AgentNode(
        id="selective", name="Selective", node_type="agent",
        interests=["important.*"],
    )
    bb = InMemoryBlackboard()
    bus = InMemoryMessageBus()
    runtime = SwarmRuntime(tree=agent, blackboard=bb, bus=bus, provider=provider)

    await runtime.start()
    await asyncio.sleep(0.05)

    # Write to an uninterested key
    await bb.write("noise.something", "irrelevant", "x")
    await asyncio.sleep(0.05)
    call_count_before = len(provider.calls)

    # Write to an interested key
    await bb.write("important.update", "relevant", "chief")
    # Wait longer than the agent's idle sleep (0.5s) so it detects the change
    await asyncio.sleep(0.6)

    assert len(provider.calls) == call_count_before + 1
    await runtime.stop()


@pytest.mark.asyncio
async def test_stop_cancels_all_tasks():
    agent = AgentNode(id="a", name="A", node_type="agent")
    runtime = SwarmRuntime(
        tree=agent,
        blackboard=InMemoryBlackboard(),
        bus=InMemoryMessageBus(),
        provider=MockProvider(),
    )
    await runtime.start()
    await runtime.stop()
    assert runtime._tasks["a"].done()
