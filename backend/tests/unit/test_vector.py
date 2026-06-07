import pytest
from storyloom.memory.vector import VectorStore

# sqlite-vec may or may not be installed
try:
    import sqlite_vec
    has_vec = True
except ImportError:
    has_vec = False


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
@pytest.mark.skipif(not has_vec, reason="sqlite-vec not installed")
async def test_vector_search_when_vec_available(vstore):
    """This test only runs when sqlite-vec is available."""
    await vstore.add_entry("proj-1", "The hero enters the dark forest", {"type": "scene"})
    await vstore.add_entry("proj-1", "The villain plans revenge", {"type": "scene"})
    results = await vstore.search("proj-1", "hero")
    assert len(results) >= 1
