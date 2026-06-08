"""tests/unit/swarm/test_models.py"""
import pytest
from storyloom.swarm.models import AgentNode, Message, BlackboardEntry, RuntimeEvent


class TestAgentNode:
    def test_create_agent_node(self):
        node = AgentNode(id="w1", name="Writer-1", node_type="agent")
        assert node.id == "w1"
        assert node.name == "Writer-1"
        assert node.node_type == "agent"
        assert node.children == []
        assert node.parent_id is None
        assert node.interests == []

    def test_create_group_with_children(self):
        child = AgentNode(id="c1", name="Child", node_type="agent")
        parent = AgentNode(
            id="g1", name="Group", node_type="group",
            children=[child],
        )
        assert child in parent.children
        assert parent.node_type == "group"

    def test_walk_flat(self):
        """walk() yields all nodes in DFS order."""
        leaf1 = AgentNode(id="a", name="A", node_type="agent")
        leaf2 = AgentNode(id="b", name="B", node_type="agent")
        group = AgentNode(id="g", name="G", node_type="group", children=[leaf1, leaf2])
        ids = [n.id for n in group.walk()]
        assert ids == ["g", "a", "b"]

    def test_walk_nested(self):
        inner = AgentNode(id="inner", name="Inner", node_type="agent",
            children=[AgentNode(id="deep", name="Deep", node_type="agent")])
        outer = AgentNode(id="outer", name="Outer", node_type="group", children=[inner])
        ids = [n.id for n in outer.walk()]
        assert ids == ["outer", "inner", "deep"]

    def test_deep_copy(self):
        child = AgentNode(id="c", name="C", node_type="agent")
        original = AgentNode(id="p", name="P", node_type="group", children=[child])
        copied = original.deep_copy()
        assert copied.id == original.id
        assert copied.children[0].id == original.children[0].id
        # Mutate original — copy must be unaffected
        original.children[0].id = "changed"
        assert copied.children[0].id == "c"

    def test_find_by_id(self):
        target = AgentNode(id="target", name="Target", node_type="agent")
        root = AgentNode(id="root", name="Root", node_type="group", children=[target])
        assert root.find("target") is target
        assert root.find("nonexistent") is None


class TestMessage:
    def test_create_message(self):
        msg = Message(
            from_id="writer-1",
            to_id="continuity",
            msg_type="chapter_done",
            payload={"chapter": 1, "word_count": 2500},
        )
        assert msg.from_id == "writer-1"
        assert msg.to_id == "continuity"
        assert msg.msg_type == "chapter_done"
        assert msg.payload["word_count"] == 2500

    def test_broadcast_message(self):
        msg = Message(from_id="chief", msg_type="decision", payload={"verdict": "approved"})
        assert msg.to_id is None
        assert msg.to_group is None

    def test_group_message(self):
        msg = Message(from_id="chief", msg_type="order", to_group="writing-group",
                      payload={"action": "revise"})
        assert msg.to_group == "writing-group"


class TestBlackboardEntry:
    def test_create_entry(self):
        entry = BlackboardEntry(key="drafts.ch1", value="Chapter 1 text...", writer_id="writer-1")
        assert entry.key == "drafts.ch1"
        assert entry.version == 1
        assert entry.writer_id == "writer-1"

    def test_version_default_and_override(self):
        e1 = BlackboardEntry(key="x", value="v1", writer_id="a")
        assert e1.version == 1
        # Version auto-increment is handled by the blackboard store
        e2 = BlackboardEntry(key="x", value="v2", writer_id="b", version=2)
        assert e2.version == 2


class TestRuntimeEvent:
    def test_create_event(self):
        ev = RuntimeEvent(
            event_type="node_start",
            node_id="planner",
            timestamp=1234.0,
            data={"task": "plan_arc"},
        )
        assert ev.event_type == "node_start"

    def test_all_event_types(self):
        for t in ("node_start", "node_complete", "node_failed", "llm_call", "message_sent", "blackboard_write"):
            ev = RuntimeEvent(event_type=t, node_id="x")
