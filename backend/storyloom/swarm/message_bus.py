"""backend/storyloom/swarm/message_bus.py"""
import asyncio
import time
from collections import defaultdict
from typing import AsyncIterator

from storyloom.swarm.models import Message


class InMemoryMessageBus:
    """In-memory message bus for agent-to-agent communication."""

    def __init__(self):
        self._inboxes: dict[str, list[Message]] = defaultdict(list)
        self._timestamps: dict[str, list[float]] = defaultdict(list)
        self._subscribers: dict[str, list[asyncio.Event]] = defaultdict(list)
        # Global broadcast messages (no to_id, no to_group)
        self._broadcast_msgs: list[Message] = []
        self._broadcast_times: list[float] = []
        self._consumed_broadcasts: dict[str, set[int]] = defaultdict(set)

    async def send(self, msg: Message) -> None:
        """Deliver a message to its target(s)."""
        now = time.time()
        if msg.to_id:
            self._inboxes[msg.to_id].append(msg)
            self._timestamps[msg.to_id].append(now)
            self._notify_subscriber(msg.to_id)
        elif msg.to_group:
            self._broadcast_msgs.append(msg)
            self._broadcast_times.append(now)
            self._notify_subscriber(f"__group__{msg.to_group}")
        else:
            # Global broadcast — deliver to every agent
            self._broadcast_msgs.append(msg)
            self._broadcast_times.append(now)
            # Wake all subscribers so they pick up the broadcast
            for subs in self._subscribers.values():
                for evt in subs:
                    evt.set()

    def _notify_subscriber(self, agent_id: str) -> None:
        for evt in self._subscribers.get(agent_id, []):
            evt.set()

    async def receive(self, agent_id: str, since: float = 0) -> list[Message]:
        """Get all messages for agent_id, optionally since a timestamp."""
        msgs = list(self._inboxes.get(agent_id, []))
        timestamps = list(self._timestamps.get(agent_id, []))

        # Include unconsumed global broadcasts
        for i in range(len(self._broadcast_msgs)):
            if i in self._consumed_broadcasts[agent_id]:
                continue
            self._consumed_broadcasts[agent_id].add(i)
            bm = self._broadcast_msgs[i]
            bt = self._broadcast_times[i]
            # Only include true global broadcasts (no to_id, no to_group)
            if bm.to_id is None and bm.to_group is None:
                msgs.append(bm)
                timestamps.append(bt)

        if not since:
            return msgs
        return [m for m, t in zip(msgs, timestamps) if t > since]

    async def subscribe(self, agent_id: str) -> AsyncIterator[Message]:
        """Async stream of incoming messages for agent_id."""
        while True:
            # Drain inbox
            while self._inboxes.get(agent_id):
                yield self._inboxes[agent_id].pop(0)
            # Also drain any unconsumed global broadcasts
            for i in range(len(self._broadcast_msgs)):
                if i in self._consumed_broadcasts[agent_id]:
                    continue
                bm = self._broadcast_msgs[i]
                if bm.to_id is None and bm.to_group is None:
                    self._consumed_broadcasts[agent_id].add(i)
                    yield bm
            evt = asyncio.Event()
            self._subscribers[agent_id].append(evt)
            try:
                await evt.wait()
            finally:
                self._subscribers[agent_id].remove(evt)

    async def subscribe_group(self, group_id: str) -> AsyncIterator[Message]:
        """Async stream of group-addressed messages."""
        key = f"__group__{group_id}"
        while True:
            for msg in self._broadcast_msgs:
                if msg.to_group == group_id:
                    yield msg
            evt = asyncio.Event()
            self._subscribers[key].append(evt)
            try:
                await evt.wait()
            finally:
                self._subscribers[key].remove(evt)
