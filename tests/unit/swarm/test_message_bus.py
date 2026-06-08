"""tests/unit/swarm/test_message_bus.py"""
import asyncio
import time

import pytest
from storyloom.swarm.models import Message
from storyloom.swarm.message_bus import InMemoryMessageBus


@pytest.mark.asyncio
async def test_send_and_receive():
    bus = InMemoryMessageBus()
    sent = Message(from_id="a", to_id="b", msg_type="hello", payload="hi")
    await bus.send(sent)
    msgs = await bus.receive("b")
    assert len(msgs) == 1
    assert msgs[0].msg_type == "hello"
    assert msgs[0].payload == "hi"


@pytest.mark.asyncio
async def test_receive_empty():
    bus = InMemoryMessageBus()
    msgs = await bus.receive("nobody")
    assert msgs == []


@pytest.mark.asyncio
async def test_agent_receives_only_own_messages():
    bus = InMemoryMessageBus()
    await bus.send(Message(from_id="x", to_id="a", msg_type="for_a"))
    await bus.send(Message(from_id="x", to_id="b", msg_type="for_b"))
    msgs_a = await bus.receive("a")
    msgs_b = await bus.receive("b")
    assert len(msgs_a) == 1 and msgs_a[0].msg_type == "for_a"
    assert len(msgs_b) == 1 and msgs_b[0].msg_type == "for_b"


@pytest.mark.asyncio
async def test_broadcast():
    bus = InMemoryMessageBus()
    await bus.send(Message(from_id="chief", msg_type="alert", payload="fire"))
    msgs_a = await bus.receive("a")
    msgs_b = await bus.receive("b")
    assert len(msgs_a) == 1 and msgs_a[0].payload == "fire"
    assert len(msgs_b) == 1 and msgs_b[0].payload == "fire"


@pytest.mark.asyncio
async def test_receive_since():
    bus = InMemoryMessageBus()
    await bus.send(Message(from_id="x", to_id="a", msg_type="first"))
    await asyncio.sleep(0.02)
    after = time.time()
    await bus.send(Message(from_id="x", to_id="a", msg_type="second"))
    new = await bus.receive("a", since=after)
    assert len(new) == 1
    assert new[0].msg_type == "second"


@pytest.mark.asyncio
async def test_subscribe_stream():
    bus = InMemoryMessageBus()
    inbox = []

    async def reader():
        async for msg in bus.subscribe("a"):
            inbox.append(msg)
            if len(inbox) >= 2:
                break

    task = asyncio.create_task(reader())
    await asyncio.sleep(0.01)
    await bus.send(Message(from_id="x", to_id="a", msg_type="m1"))
    await bus.send(Message(from_id="y", to_id="a", msg_type="m2"))
    await asyncio.wait_for(task, timeout=2.0)
    assert len(inbox) == 2
