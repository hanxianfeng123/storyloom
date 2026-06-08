"""tests/unit/swarm/novel/test_prompts.py"""
from storyloom.swarm.novel.prompts import (
    PLANNER_PROMPT, WRITER_PROMPT, CONTINUITY_PROMPT,
    EDITOR_PROMPT, QUALITY_PROMPT, CHIEF_PROMPT,
)


def test_planner_prompt_contains_chinese():
    assert "篇章弧" in PLANNER_PROMPT or "规划" in PLANNER_PROMPT

def test_writer_prompt_has_structure():
    assert "章节" in WRITER_PROMPT
    assert len(WRITER_PROMPT) > 100

def test_chief_prompt_has_decision():
    assert "批准" in CHIEF_PROMPT or "approved" in CHIEF_PROMPT.lower()

def test_quality_prompt_has_dimensions():
    assert "情节" in QUALITY_PROMPT or "plot" in QUALITY_PROMPT.lower()

def test_all_prompts_defined():
    prompts = [PLANNER_PROMPT, WRITER_PROMPT, CONTINUITY_PROMPT,
               EDITOR_PROMPT, QUALITY_PROMPT, CHIEF_PROMPT]
    for p in prompts:
        assert len(p) > 50, f"Prompt too short: {p[:30]}"
