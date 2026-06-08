"""tests/integration/swarm/test_novel_arc.py"""
import asyncio

import pytest
from storyloom.swarm.novel.orch import run_story_arc
from storyloom.swarm.provider import AgentProvider


class MockProvider(AgentProvider):
    """Deterministic mock for integration tests.

    Uses unique substring checks on system_prompt for each agent role.
    Order is important -- more specific checks go first.

    Includes an ``await asyncio.sleep(0)`` to yield control so the
    event loop can schedule other tasks (simulating the natural
    yield of a real LLM provider).
    """

    def __init__(self):
        self.call_count = 0

    async def step(self, system_prompt, user_prompt, llm_config=None) -> str:
        self.call_count += 1
        # Yield to allow the event loop to schedule other tasks.
        # Real LLM providers yield naturally during network I/O.
        await asyncio.sleep(0)
        # Chief (check first -- most important for test assertions)
        if "总编辑" in system_prompt:
            return '{"decision": "approved", "summary": "All good"}'
        # Quality
        if "质量评审" in system_prompt:
            return "pass"
        # Continuity
        if "连续性" in system_prompt:
            return "一致性通过"
        # Planner (uses "规划" which only appears in PLANNER_PROMPT)
        if "规划" in system_prompt:
            return '{"outline": {"ch1": "intro", "ch2": "conflict", "ch3": "resolution"}}'
        # Writer
        if "小说作家" in system_prompt or "写手" in system_prompt:
            return f"Chapter content from call {self.call_count}"
        # Reader / fallback
        return f"mock response {self.call_count}"


@pytest.mark.asyncio
async def test_run_story_arc_basic():
    """Happy path: all agents respond, chief approves."""
    result = await run_story_arc(
        story_bible={"title": "测试", "genre": "奇幻", "summary": "一个测试故事"},
        character_cards=[{"name": "Alice", "role": "hero"}],
        world_state={"settings": {}},
        chapter_history=[],
        chapter_count=2,
        provider=MockProvider(),
        timeout=30.0,
    )
    assert result.status == "completed"
    assert result.decision == "approved"


@pytest.mark.asyncio
async def test_run_story_arc_with_reader_reviews():
    """Arc runs with reader agents included."""
    readers = [
        {"id": "teen", "perspective": "16岁女高中生", "model": "mock"},
        {"id": "prof", "perspective": "退休教授", "temperature": 0.3},
    ]
    result = await run_story_arc(
        story_bible={"title": "T", "genre": "SF"},
        character_cards=[],
        world_state={},
        chapter_history=[],
        chapter_count=1,
        reader_configs=readers,
        provider=MockProvider(),
        timeout=30.0,
    )
    assert result.status == "completed"
