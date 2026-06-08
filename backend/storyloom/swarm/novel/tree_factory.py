"""backend/storyloom/swarm/novel/tree_factory.py"""
from storyloom.swarm.models import AgentNode, NodeType
from storyloom.swarm.novel import prompts


def build_novel_arc_tree(
    chapter_count: int = 3,
    planner_model: str = "anthropic/claude-sonnet-4-20250514",
    writer_model: str = "deepseek/deepseek-chat",
    editor_model: str = "anthropic/claude-sonnet-4-20250514",
    chief_model: str = "anthropic/claude-sonnet-4-20250514",
) -> AgentNode:
    """Build the agent tree for story arc generation.

    The tree structure defines organizational hierarchy only.
    No execution order -- agents decide when to act based on
    blackboard state and messages.
    """
    reader_group = AgentNode(
        id="readers", name="读者审阅团", node_type=NodeType.GROUP,
        children=[],  # Populated from DB at runtime
    )

    return AgentNode(
        id="arc-master", name="篇章弧生成", node_type=NodeType.GROUP,
        children=[
            # Tier 1: Writing Group
            AgentNode(
                id="writing-group", name="写作组", node_type=NodeType.GROUP,
                children=[
                    AgentNode(
                        id="planner", name="篇章规划师", node_type=NodeType.AGENT,
                        system_prompt=prompts.PLANNER_PROMPT,
                        llm_config={"model": planner_model, "temperature": 0.7, "max_tokens": 4096},
                        interests=["story_bible", "chapter_history",
                                   "world_state", "character_cards",
                                   "target", "revision_request"],
                    ),
                    AgentNode(
                        id="writers", name="写手池", node_type=NodeType.POOL,
                        pool_size=chapter_count,
                        system_prompt=prompts.WRITER_PROMPT,
                        llm_config={"model": writer_model, "temperature": 0.8, "max_tokens": 8192},
                        interests=["arc_outline", "revision_request",
                                   "conflict_report", "editor_feedback"],
                    ),
                ],
            ),
            # Tier 2: Editorial Group
            AgentNode(
                id="editorial-group", name="编辑组", node_type=NodeType.GROUP,
                children=[
                    AgentNode(
                        id="continuity", name="连续性检查", node_type=NodeType.AGENT,
                        system_prompt=prompts.CONTINUITY_PROMPT,
                        llm_config={"model": editor_model, "temperature": 0.3, "max_tokens": 2048},
                        interests=["drafts.*", "arc_outline",
                                   "world_state", "character_cards"],
                    ),
                    AgentNode(
                        id="editor", name="润色编辑", node_type=NodeType.AGENT,
                        system_prompt=prompts.EDITOR_PROMPT,
                        llm_config={"model": editor_model, "temperature": 0.3, "max_tokens": 4096},
                        interests=["drafts.*", "conflict_report"],
                    ),
                    AgentNode(
                        id="quality", name="质量评审", node_type=NodeType.AGENT,
                        system_prompt=prompts.QUALITY_PROMPT,
                        llm_config={"model": editor_model, "temperature": 0.3, "max_tokens": 2048},
                        interests=["drafts.*", "edited_chapters.*",
                                   "conflict_report"],
                    ),
                ],
            ),
            # Tier 3: Editor-in-Chief
            AgentNode(
                id="chief", name="总编", node_type=NodeType.AGENT,
                system_prompt=prompts.CHIEF_PROMPT,
                llm_config={"model": chief_model, "temperature": 0.3, "max_tokens": 2048},
                interests=["quality_report", "conflict_report",
                           "drafts.*", "edited_chapters.*",
                           "reader_review.*", "responses.*"],
            ),
            # Reader Review Group (populated at runtime from DB)
            reader_group,
        ],
    )
