"""tests/unit/swarm/novel/test_tree_factory.py"""
import pytest
from storyloom.swarm.novel.tree_factory import build_novel_arc_tree
from storyloom.swarm.novel.prompts import PLANNER_PROMPT, WRITER_PROMPT


def test_build_novel_arc_tree():
    tree = build_novel_arc_tree(chapter_count=3)
    assert tree.id == "arc-master"
    assert tree.node_type == "group"


def test_tree_contains_all_layers():
    tree = build_novel_arc_tree(3)
    assert tree.find("writing-group") is not None
    assert tree.find("editorial-group") is not None
    assert tree.find("chief") is not None


def test_writing_group_has_planner_and_writers():
    tree = build_novel_arc_tree(3)
    assert tree.find("planner") is not None
    assert tree.find("writers") is not None


def test_writers_pool_size_matches_chapter_count():
    tree = build_novel_arc_tree(5)
    writers = tree.find("writers")
    assert writers.pool_size == 5


def test_editorial_group_has_continuity_editor_quality():
    tree = build_novel_arc_tree(3)
    assert tree.find("continuity") is not None
    assert tree.find("editor") is not None
    assert tree.find("quality") is not None


def test_planner_has_correct_prompt():
    tree = build_novel_arc_tree(3)
    planner = tree.find("planner")
    assert PLANNER_PROMPT in planner.system_prompt
