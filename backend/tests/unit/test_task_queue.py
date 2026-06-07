import asyncio
import pytest
from storyloom.core.task_queue import TaskQueue


async def wait_for_result(queue, task_id, timeout=5):
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < timeout:
        status = queue.get_status(task_id)
        if status == "completed":
            return queue.get_result(task_id)
        if status == "failed":
            raise RuntimeError(queue.get_result(task_id))
        await asyncio.sleep(0.01)
    raise TimeoutError(f"Task {task_id} did not complete in {timeout}s")


@pytest.mark.asyncio
async def test_submit_and_wait():
    queue = TaskQueue()
    task = await queue.submit(asyncio.sleep(0.01, result="done"))
    result = await wait_for_result(queue, task.id)
    assert result == "done"


@pytest.mark.asyncio
async def test_status_tracking():
    queue = TaskQueue()
    async def slow_task():
        await asyncio.sleep(0.05)
        return "slow done"
    task = await queue.submit(slow_task())
    status = queue.get_status(task.id)
    assert status in ("running", "completed")
    while queue.get_status(task.id) == "running":
        await asyncio.sleep(0.01)
    assert queue.get_status(task.id) == "completed"
