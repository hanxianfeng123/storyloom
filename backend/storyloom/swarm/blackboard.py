"""backend/storyloom/swarm/blackboard.py"""
import asyncio
import fnmatch
import time
from collections import defaultdict
from typing import Any, AsyncIterator

from storyloom.swarm.models import BlackboardEntry


class BlackboardEvent:
    """Notification sent to watchers when a key changes."""

    def __init__(self, key: str, value: Any, writer_id: str, version: int):
        self.key = key
        self.value = value
        self.writer_id = writer_id
        self.version = version


class InMemoryBlackboard:
    """Shared workspace where agents read and write structured data."""

    def __init__(self):
        self._store: dict[str, Any] = {}
        self._history: dict[str, list[BlackboardEntry]] = defaultdict(list)
        self._listeners: list[asyncio.Event] = []
        self._lock = asyncio.Lock()

    async def read(self, key: str) -> Any:
        return self._store.get(key)

    async def write(self, key: str, value: Any, writer_id: str) -> BlackboardEvent:
        async with self._lock:
            self._store[key] = value
            version = len(self._history[key]) + 1
            self._history[key].append(
                BlackboardEntry(
                    key=key,
                    value=value,
                    writer_id=writer_id,
                    timestamp=time.time(),
                    version=version,
                )
            )
            event = BlackboardEvent(key, value, writer_id, version)
            for evt in self._listeners:
                evt.set()
        return event

    async def watch(self, pattern: str) -> AsyncIterator[BlackboardEvent]:
        """Yield events for keys matching pattern (fnmatch)."""
        while True:
            evt = asyncio.Event()
            self._listeners.append(evt)
            try:
                while True:
                    await evt.wait()
                    evt.clear()
                    for key, value in list(self._store.items()):
                        if fnmatch.fnmatch(key, pattern):
                            hist = self._history[key]
                            last = hist[-1]
                            yield BlackboardEvent(
                                key=key,
                                value=value,
                                writer_id=last.writer_id,
                                version=last.version,
                            )
            finally:
                self._listeners.remove(evt)

    async def history(self, key: str) -> list[BlackboardEntry]:
        return list(self._history.get(key, []))

    async def entries_since(self, since_time: float) -> list[BlackboardEvent]:
        """Return all entries written after since_time (across all keys)."""
        events = []
        for key, entries in self._history.items():
            for entry in entries:
                if entry.timestamp > since_time:
                    events.append(
                        BlackboardEvent(
                            key=key,
                            value=entry.value,
                            writer_id=entry.writer_id,
                            version=entry.version,
                        )
                    )
        return events
