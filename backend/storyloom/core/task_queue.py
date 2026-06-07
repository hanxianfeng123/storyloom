import asyncio
import uuid
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaskInfo:
    id: str
    status: str  # running | completed | failed
    created_at: float
    completed_at: float | None = None
    result: Any = None
    error: str | None = None


class TaskQueue:
    def __init__(self):
        self._tasks: dict[str, TaskInfo] = {}

    async def submit(self, coro) -> TaskInfo:
        task_id = uuid.uuid4().hex[:12]
        info = TaskInfo(id=task_id, status="running", created_at=time.time())
        self._tasks[task_id] = info
        asyncio.create_task(self._execute(task_id, coro, info))
        return info

    async def _execute(self, task_id: str, coro, info: TaskInfo):
        try:
            result = await coro
            info.status = "completed"
            info.result = result
        except Exception as e:
            info.status = "failed"
            info.error = str(e)
        finally:
            info.completed_at = time.time()

    async def run(self, fn) -> Any:
        if asyncio.iscoroutinefunction(fn):
            coro = fn()
        elif asyncio.iscoroutine(fn):
            coro = fn
        else:
            result = fn()
            if asyncio.iscoroutine(result):
                coro = result
            else:
                async def wrapper():
                    return result
                coro = wrapper()
        info = await self.submit(coro)
        while info.status == "running":
            await asyncio.sleep(0.1)
        if info.status == "failed":
            raise RuntimeError(info.error)
        return info.result

    def get_status(self, task_id: str) -> str | None:
        info = self._tasks.get(task_id)
        return info.status if info else None
