import pytest
from datetime import datetime
from storyloom.memory.models.character import Character, CharacterState
from storyloom.memory.models.plot_thread import PlotThread
from storyloom.memory.models.world_state import WorldStateEntry
from storyloom.memory.models.chapter import ChapterRecord


def test_character_creation():
    c = Character(name="Alice", role="protagonist", location="Forest", status="active")
    assert c.name == "Alice"
    assert c.status == "active"


def test_plot_thread_dormant_detection():
    thread = PlotThread(name="Mystery Box", status="active", first_chapter=1, target_chapter=10)
    assert thread.last_seen_chapter is None  # Not seen yet


def test_world_state_entry():
    w = WorldStateEntry(key="season", value="autumn", updated_at=datetime.now())
    assert w.key == "season"
    assert w.value == "autumn"


def test_chapter_record():
    ch = ChapterRecord(number=1, title="The Beginning", status="draft", word_count=1500)
    assert ch.status == "draft"
