import asyncio

import pytest
from storyloom.core.task_queue import TaskQueue


@pytest.mark.asyncio
async def test_submit_and_wait():
    queue = TaskQueue()
    result = await queue.run(lambda: "done")
    assert result == "done"


@pytest.mark.asyncio
async def test_status_tracking():
    queue = TaskQueue()
    async def slow_task():
        import asyncio
        await asyncio.sleep(0.05)
        return "slow done"
    task = await queue.submit(slow_task())
    status = queue.get_status(task.id)
    assert status in ("running", "completed")
    # Wait for completion
    while queue.get_status(task.id) == "running":
        await asyncio.sleep(0.01)
    assert queue.get_status(task.id) == "completed"
