import pytest
from storyloom.memory.store import SQLiteStore
from storyloom.memory.models.character import Character


@pytest.fixture
async def store(tmp_path):
    db_path = str(tmp_path / "test.db")
    s = SQLiteStore(db_path)
    await s.connect()
    yield s
    s.close()


@pytest.mark.asyncio
async def test_save_and_get_character(store):
    char = Character(name="Alice", role="protagonist", location="Forest")
    await store.save_character("proj-1", char)
    loaded = await store.get_character("proj-1", "Alice")
    assert loaded is not None
    assert loaded.name == "Alice"
    assert loaded.location == "Forest"


@pytest.mark.asyncio
async def test_get_character_not_found(store):
    loaded = await store.get_character("proj-1", "NonExistent")
    assert loaded is None


@pytest.mark.asyncio
async def test_list_characters(store):
    char1 = Character(name="Alice", role="protagonist")
    char2 = Character(name="Bob", role="antagonist")
    await store.save_character("proj-1", char1)
    await store.save_character("proj-1", char2)
    chars = await store.list_characters("proj-1")
    assert len(chars) == 2
