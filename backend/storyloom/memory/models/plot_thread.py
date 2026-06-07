from pydantic import BaseModel


class PlotThread(BaseModel):
    name: str
    status: str = "active"  # active | resolved | abandoned
    first_chapter: int
    target_chapter: int | None = None
    last_seen_chapter: int | None = None
    description: str = ""
