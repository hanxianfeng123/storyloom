"""tests/unit/swarm/test_agent_repo.py"""
import pytest
from storyloom.db.agent_repo import AgentRepo
from storyloom.swarm.models import AgentNode


@pytest.mark.asyncio
async def test_save_and_load_tree():
    repo = AgentRepo(":memory:")
    await repo.initialize()

    tree = AgentNode(id="root", name="Root", node_type="group",
        children=[
            AgentNode(id="leaf1", name="Leaf 1", node_type="agent",
                      system_prompt="You are leaf 1",
                      llm_config={"model": "m1"}, interests=["a.*"]),
            AgentNode(id="leaf2", name="Leaf 2", node_type="agent"),
        ])
    await repo.save_tree("project_1", tree)

    loaded = await repo.load_tree("project_1")
    assert loaded is not None
    assert loaded.id == "root"
    leaf1 = loaded.find("leaf1")
    assert leaf1 is not None
    assert leaf1.system_prompt == "You are leaf 1"
    assert leaf1.llm_config == {"model": "m1"}
    assert leaf1.interests == ["a.*"]
    leaf2 = loaded.find("leaf2")
    assert leaf2 is not None


@pytest.mark.asyncio
async def test_load_nonexistent():
    repo = AgentRepo(":memory:")
    await repo.initialize()
    tree = await repo.load_tree("nonexistent")
    assert tree is None


@pytest.mark.asyncio
async def test_update_node_in_tree():
    repo = AgentRepo(":memory:")
    await repo.initialize()
    tree = AgentNode(id="root", name="Root", node_type="group",
        children=[AgentNode(id="a", name="A", node_type="agent", system_prompt="old")])
    await repo.save_tree("p1", tree)

    await repo.update_node("p1", "a", {"system_prompt": "new", "llm_config": {"model": "x"}})
    loaded = await repo.load_tree("p1")
    updated = loaded.find("a")
    assert updated.system_prompt == "new"
    assert updated.llm_config == {"model": "x"}
