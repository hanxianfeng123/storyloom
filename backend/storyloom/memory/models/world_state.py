from pydantic import BaseModel
from datetime import datetime


class WorldStateEntry(BaseModel):
    key: str
    value: str
    updated_at: datetime
    chapter_number: int | None = None
