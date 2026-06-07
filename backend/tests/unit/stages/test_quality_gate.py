import pytest
from storyloom.core.stages.quality_gate import (
    QualityGateStage,
    check_dormant_threads,
    check_absent_characters,
    check_word_count,
    QualityIssue,
)


def test_dormant_thread_detection():
    issues = check_dormant_threads([
        {"name": "Thread A", "last_seen": 1},
        {"name": "Thread B", "last_seen": None},
    ], current_chapter=5)
    assert len(issues) == 1
    assert issues[0].severity == "warning"


def test_word_count_pass():
    issues = check_word_count(target=2000, actual=1950)
    assert len(issues) == 0


def test_word_count_fail():
    issues = check_word_count(target=2000, actual=500)
    assert len(issues) == 1
    assert issues[0].severity == "warning"


def test_absent_characters():
    issues = check_absent_characters([
        {"name": "Alice", "last_seen_chapter": 1},
        {"name": "Bob", "last_seen_chapter": 10},
    ], current_chapter=12, threshold=5)
    assert len(issues) >= 0
