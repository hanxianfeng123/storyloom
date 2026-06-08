"""backend/storyloom/swarm/novel/orch.py"""
import asyncio
import json
import logging

from storyloom.swarm.models import AgentNode
from storyloom.swarm.blackboard import InMemoryBlackboard
from storyloom.swarm.message_bus import InMemoryMessageBus
from storyloom.swarm.runtime import SwarmRuntime
from storyloom.swarm.novel.tree_factory import build_novel_arc_tree
from storyloom.swarm.novel.prompts import READER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class ArcResult:
    """Result of a story arc run."""

    def __init__(
        self,
        status: str,
        chapters: dict | None = None,
        decision: str = "",
        summary: str = "",
    ):
        self.status = status
        self.chapters = chapters or {}
        self.decision = decision
        self.summary = summary


async def _first_event(agen):
    """Return the first event from an async generator."""
    async for event in agen:
        return event


async def run_story_arc(
    story_bible: dict,
    character_cards: list[dict],
    world_state: dict,
    chapter_history: list[dict],
    chapter_count: int = 3,
    reader_configs: list[dict] | None = None,
    provider=None,
    timeout: float = 600.0,
) -> ArcResult:
    """Execute a story arc using the agent swarm.

    All agents run autonomously. This function:
    1. Builds the agent tree
    2. Seeds the blackboard with initial context
    3. Starts all agent loops
    4. Waits for the chief's decision
    """
    tree = build_novel_arc_tree(chapter_count=chapter_count)
    bb = InMemoryBlackboard()
    bus = InMemoryMessageBus()
    runtime = SwarmRuntime(tree=tree, blackboard=bb, bus=bus, provider=provider)

    # Add reader agents from config
    for cfg in reader_configs or []:
        perspective = cfg.get("perspective", "普通读者")
        prompt = READER_PROMPT_TEMPLATE.format(perspective=perspective)
        reader_node = AgentNode(
            id=f"reader.{cfg.get('id', perspective)}",
            name=perspective,
            node_type="agent",
            system_prompt=prompt,
            llm_config={
                "model": cfg.get("model", "anthropic/claude-sonnet-4-20250514"),
                "temperature": cfg.get("temperature", 0.7),
            },
            interests=["drafts.*", "request_review"],
        )
        readers_node = tree.find("readers")
        if readers_node is not None:
            readers_node.children.append(reader_node)

    # Set up the chief response watcher BEFORE starting agents
    # so we don't miss the event if agents write before the listener is registered.
    watch_iter = bb.watch("responses.chief").__aiter__()

    # Seed initial context
    await bb.write("story_bible", story_bible, "system")
    await bb.write("character_cards", character_cards, "system")
    await bb.write("world_state", world_state, "system")
    await bb.write("chapter_history", chapter_history, "system")
    await bb.write("target", {"chapters": chapter_count}, "system")

    # Start the swarm
    await runtime.start()

    try:
        # Wait for chief's response with timeout
        event = await asyncio.wait_for(
            watch_iter.__anext__(),
            timeout=timeout,
        )
        chief_response = event.value

        # Parse the chief's decision
        decision = ""
        summary = ""
        if isinstance(chief_response, str):
            try:
                parsed = json.loads(chief_response)
                decision = parsed.get("decision", "")
                summary = parsed.get("summary", "")
            except (json.JSONDecodeError, TypeError):
                summary = chief_response[:500]

        # Collect results
        chapters = {}
        for i in range(chapter_count):
            content = await bb.read(f"drafts.ch{i + 1}")
            if content:
                chapters[f"ch{i + 1}"] = content

        return ArcResult(
            status="completed",
            chapters=chapters,
            decision=decision,
            summary=summary,
        )

    except asyncio.TimeoutError:
        logger.warning("Story arc timed out after %ss", timeout)
        return ArcResult(status="timeout")
    finally:
        await runtime.stop()
