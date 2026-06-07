import asyncio
import uuid
import time
from dataclasses import dataclass
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
    """Simple in-process async task queue."""

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

    def get_status(self, task_id: str) -> str | None:
        info = self._tasks.get(task_id)
        return info.status if info else None

    def get_result(self, task_id: str) -> Any:
        info = self._tasks.get(task_id)
        if info is None:
            return None
        if info.status == "failed":
            raise RuntimeError(info.error or "Unknown error")
        return info.result
