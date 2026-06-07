from abc import ABC, abstractmethod
from pydantic import BaseModel


class PublishResult(BaseModel):
    path: str
    format: str
    size_bytes: int


class OutputAdapter(ABC):
    @abstractmethod
    async def publish(self, project_id: str, chapter_number: int, content: str) -> PublishResult:
        ...
