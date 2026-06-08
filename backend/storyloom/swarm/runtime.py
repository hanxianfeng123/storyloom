"""backend/storyloom/swarm/runtime.py"""
import asyncio
import fnmatch
import logging
import time
from typing import Callable

from storyloom.swarm.models import AgentNode, Message, RuntimeEvent
from storyloom.swarm.blackboard import InMemoryBlackboard
from storyloom.swarm.message_bus import InMemoryMessageBus
from storyloom.swarm.provider import AgentProvider

logger = logging.getLogger(__name__)


class AgentContext:
    """Holds everything an agent needs during its lifecycle."""

    def __init__(
        self,
        agent_id: str,
        node: AgentNode,
        blackboard: InMemoryBlackboard,
        bus: InMemoryMessageBus,
        provider: AgentProvider,
        event_callback: Callable[[RuntimeEvent], None] | None = None,
    ):
        self.agent_id = agent_id
        self.node = node
        self.blackboard = blackboard
        self.bus = bus
        self.provider = provider
        self.event_callback = event_callback or (lambda _: None)
        self._cancelled = False
        self._last_check_time: float = 0.0

    def cancel(self):
        """Signal the agent loop to stop."""
        self._cancelled = True


class SwarmRuntime:
    """Manages agent lifecycle and message routing.

    Walks the AgentNode tree, creates one asyncio.Task per agent/pool node,
    and orchestrates their perceive->think->act loops.
    """

    def __init__(
        self,
        tree: AgentNode,
        blackboard: InMemoryBlackboard | None = None,
        bus: InMemoryMessageBus | None = None,
        provider: AgentProvider | None = None,
        event_callback: Callable[[RuntimeEvent], None] | None = None,
    ):
        self.tree = tree
        self.blackboard = blackboard or InMemoryBlackboard()
        self.bus = bus or InMemoryMessageBus()
        self._provider = provider
        self._event_callback = event_callback
        self._tasks: dict[str, asyncio.Task] = {}
        self._contexts: dict[str, AgentContext] = {}

    async def start(self) -> None:
        """Walk the tree and start one async task per agent/pool node."""
        for node in self._walk_agents(self.tree):
            if node.node_type == "pool":
                for i in range(node.pool_size):
                    agent_id = f"{node.id}.{i}"
                    ctx = AgentContext(
                        agent_id=agent_id,
                        node=node,
                        blackboard=self.blackboard,
                        bus=self.bus,
                        provider=self._get_provider(),
                        event_callback=self._emit,
                    )
                    self._contexts[agent_id] = ctx
                    self._tasks[agent_id] = asyncio.create_task(
                        self._agent_loop(ctx), name=agent_id
                    )
            else:
                ctx = AgentContext(
                    agent_id=node.id,
                    node=node,
                    blackboard=self.blackboard,
                    bus=self.bus,
                    provider=self._get_provider(),
                    event_callback=self._emit,
                )
                self._contexts[node.id] = ctx
                if node.node_type == "agent":
                    self._tasks[node.id] = asyncio.create_task(
                        self._agent_loop(ctx), name=node.id
                    )

    def _get_provider(self) -> AgentProvider:
        if self._provider:
            return self._provider
        from storyloom.swarm.providers import LitellmProvider

        return LitellmProvider()

    def _walk_agents(self, node: AgentNode):
        """Yield all agent/pool nodes under a node (DFS)."""
        if node.node_type in ("agent", "pool"):
            yield node
        for child in node.children:
            yield from self._walk_agents(child)

    async def _agent_loop(self, ctx: AgentContext) -> None:
        """Agent's main lifecycle: perceive -> think -> act."""
        logger.info("Agent %s started", ctx.agent_id)
        while not ctx._cancelled:
            try:
                # --- Perceive ---
                msgs = await self.bus.receive(ctx.agent_id)
                changes = await self._detect_blackboard_changes(ctx)

                if not msgs and not changes:
                    await asyncio.sleep(0.5)
                    continue

                # --- Think: build prompt from what agent perceives ---
                user_prompt = self._build_prompt(ctx, msgs, changes)
                self._emit(
                    RuntimeEvent(
                        event_type="agent_decision",
                        node_id=ctx.agent_id,
                        data={"prompt_length": len(user_prompt)},
                    )
                )

                # --- Act: call LLM ---
                response = await ctx.provider.step(
                    system_prompt=ctx.node.system_prompt,
                    user_prompt=user_prompt,
                    llm_config=ctx.node.llm_config,
                )
                logger.info("Agent %s -> %s chars", ctx.agent_id, len(response))

                # --- Share: write structured response to blackboard ---
                if response.strip():
                    await ctx.blackboard.write(
                        key=f"responses.{ctx.agent_id}",
                        value=response,
                        writer_id=ctx.agent_id,
                    )

            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Agent %s crashed", ctx.agent_id)
                await asyncio.sleep(1.0)

        logger.info("Agent %s stopped", ctx.agent_id)

    async def _detect_blackboard_changes(
        self, ctx: AgentContext
    ) -> dict[str, object]:
        """Return blackboard entries written since agent's last check,
        filtered by the agent's interest patterns."""
        if not ctx.node.interests:
            return {}

        now = time.time()
        entries = await self.blackboard.entries_since(ctx._last_check_time)
        ctx._last_check_time = now

        if not entries:
            return {}

        changes = {}
        for entry in entries:
            for pattern in ctx.node.interests:
                if fnmatch.fnmatch(entry.key, pattern):
                    changes[entry.key] = entry.value
                    break
        return changes

    def _build_prompt(
        self, ctx: AgentContext, msgs: list[Message], changes: dict
    ) -> str:
        """Compose user_prompt from messages and blackboard state."""
        parts = []
        if msgs:
            parts.append("## New Messages")
            for msg in msgs:
                parts.append(f"- From {msg.from_id}: [{msg.msg_type}] {msg.payload}")
        if changes:
            parts.append("\n## Blackboard Updates")
            for key, val in changes.items():
                val_str = str(val)[:1000]
                parts.append(f"- {key}: {val_str}")
        parts.append(
            "\n## Your Response\nBased on the above, decide what to do. "
            "Write your output to the blackboard."
        )
        return "\n".join(parts)

    def _emit(self, event: RuntimeEvent) -> None:
        event.timestamp = time.time()
        event.node_id = event.node_id or ""
        if self._event_callback:
            self._event_callback(event)

    async def stop(self) -> None:
        """Stop all agent tasks."""
        for ctx in self._contexts.values():
            ctx.cancel()
        tasks = list(self._tasks.values())
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
