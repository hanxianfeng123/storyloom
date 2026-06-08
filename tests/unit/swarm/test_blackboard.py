"""tests/unit/swarm/test_blackboard.py"""
import asyncio
import time

import pytest
from storyloom.swarm.blackboard import InMemoryBlackboard


@pytest.mark.asyncio
async def test_write_and_read():
    bb = InMemoryBlackboard()
    await bb.write("drafts.ch1", "Chapter 1...", "writer-1")
    val = await bb.read("drafts.ch1")
    assert val == "Chapter 1..."


@pytest.mark.asyncio
async def test_read_nonexistent():
    bb = InMemoryBlackboard()
    val = await bb.read("nonexistent")
    assert val is None


@pytest.mark.asyncio
async def test_write_then_update():
    bb = InMemoryBlackboard()
    await bb.write("status", "pending", "chief")
    await bb.write("status", "done", "chief")
    assert await bb.read("status") == "done"


@pytest.mark.asyncio
async def test_watch_notified_on_write():
    bb = InMemoryBlackboard()
    events = []

    async def collector():
        async for ev in bb.watch("drafts.*"):
            events.append(ev)
            break  # stop after first

    task = asyncio.create_task(collector())
    await asyncio.sleep(0.01)  # let watcher register
    await bb.write("drafts.ch1", "text", "w1")
    await asyncio.wait_for(task, timeout=2.0)
    assert len(events) == 1
    assert events[0].key == "drafts.ch1"
    assert events[0].value == "text"


@pytest.mark.asyncio
async def test_watch_pattern_mismatch():
    bb = InMemoryBlackboard()
    triggered = []

    async def watcher():
        async for ev in bb.watch("outline.*"):
            triggered.append(ev)

    task = asyncio.create_task(watcher())
    await asyncio.sleep(0.01)
    await bb.write("drafts.ch1", "text", "w1")  # doesn't match
    await asyncio.sleep(0.05)
    assert len(triggered) == 0
    task.cancel()


@pytest.mark.asyncio
async def test_history():
    bb = InMemoryBlackboard()
    await bb.write("x", "v1", "a")
    await bb.write("x", "v2", "b")
    hist = await bb.history("x")
    assert len(hist) == 2
    assert hist[0].value == "v1"
    assert hist[1].value == "v2"
    assert hist[1].version == 2


@pytest.mark.asyncio
async def test_watch_wildcard():
    bb = InMemoryBlackboard()
    events = []

    async def watcher():
        async for ev in bb.watch("*"):
            events.append(ev)
            if len(events) >= 2:
                break

    task = asyncio.create_task(watcher())
    await asyncio.sleep(0.01)
    await bb.write("a", "1", "x")
    await bb.write("b", "2", "x")
    await asyncio.wait_for(task, timeout=2.0)
    assert len(events) == 2


@pytest.mark.asyncio
async def test_entries_since():
    bb = InMemoryBlackboard()
    await bb.write("a", "1", "x")
    await asyncio.sleep(0.02)
    mid = time.time()
    await asyncio.sleep(0.02)
    await bb.write("b", "2", "x")
    entries = await bb.entries_since(mid)
    assert len(entries) == 1
    assert entries[0].key == "b"
