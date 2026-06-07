import pytest
from storyloom.memory.vector import VectorStore


@pytest.fixture
async def vstore(tmp_path):
    vs = VectorStore(str(tmp_path / "vectors.db"))
    await vs.connect()
    yield vs
    vs.close()


@pytest.mark.asyncio
async def test_add_and_search(vstore):
    await vstore.add_entry("proj-1", "chapter 1 text", {"chapter": 1})
    results = await vstore.search("proj-1", "chapter")
    assert len(results) == 1
    assert results[0]["metadata"]["chapter"] == 1


@pytest.mark.asyncio
async def test_search_empty_returns_empty(vstore):
    results = await vstore.search("proj-1", "nonexistent")
    assert len(results) == 0
