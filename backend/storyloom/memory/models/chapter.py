from pydantic import BaseModel


class ChapterRecord(BaseModel):
    number: int
    title: str
    status: str = "planned"  # planned | drafting | edited | reviewed | published
    word_count: int = 0
    summary: str = ""
    outline: str = ""
    draft_path: str | None = None
