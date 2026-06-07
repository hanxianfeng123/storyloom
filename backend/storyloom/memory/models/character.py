from pydantic import BaseModel


class Character(BaseModel):
    name: str
    role: str
    personality: str = ""
    appearance: str = ""
    background: str = ""
    location: str = ""
    status: str = "active"  # active | absent | deceased
    emotional_arc: str = ""
    last_seen_chapter: int | None = None
    notes: str = ""


class CharacterState(BaseModel):
    character_name: str
    chapter_number: int
    location: str
    emotional_state: str
    relationships: dict[str, str] = {}
