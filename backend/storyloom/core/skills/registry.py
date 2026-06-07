"""Runtime skill registry — loads from DB, supports hot-reload."""

import uuid
from typing import Optional
from storyloom.memory.skill_store import SkillStore


class SkillRegistry:
    """In-memory cache of active skills, loaded from DB.

    Provides tree structure for LLM decision-making and name-based lookup
    for runtime execution.
    """

    def __init__(self, store: SkillStore):
        self._store = store
        self._by_name: dict[str, dict] = {}
        self._by_id: dict[str, dict] = {}
        self._tree: list[dict] = []

    async def load_from_db(self):
        """Load all active skills from DB into cache."""
        skills = await self._store.list_skills()
        self._by_name = {}
        self._by_id = {}
        for s in skills:
            d = s.model_dump()
            self._by_id[s.id] = d
            self._by_name[s.name] = d
        self._rebuild_tree(skills)

    def _rebuild_tree(self, skills):
        """Build nested tree from flat list using parent_id."""
        children: dict[str | None, list] = {}
        for s in skills:
            children.setdefault(s.parent_id, []).append(s.model_dump())

        def attach(node):
            node["children"] = children.get(node["id"], [])
            for c in node["children"]:
                attach(c)
            return node

        self._tree = [attach(r) for r in children.get(None, [])]

    def get(self, name: str) -> Optional[dict]:
        return self._by_name.get(name)

    def get_by_id(self, skill_id: str) -> Optional[dict]:
        return self._by_id.get(skill_id)

    def list_active(self) -> list[dict]:
        return [s for s in self._by_name.values() if s["is_active"]]

    def tree(self) -> list[dict]:
        return self._tree

    async def reload_skill(self, name: str):
        """Hot-reload a single skill after DB update."""
        skill = await self._store.get_skill_by_name(name)
        if skill:
            d = skill.model_dump()
            self._by_name[name] = d
            self._by_id[skill.id] = d
        await self.load_from_db()  # Rebuild tree

    async def seed_from_yaml(self, yaml_path: str):
        """Seed DB from YAML if skills table is empty.

        This is the initial data load when the project is first set up.
        """
        import yaml

        existing = await self._store.list_skills()
        if existing:
            return  # Already seeded

        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        def flatten_children(children, parent_id=None):
            for child in children:
                skill_id = uuid.uuid4().hex[:12]
                yield {
                    "id": skill_id,
                    "category": child.get("category", "general"),
                    "name": child["name"],
                    "parent_id": parent_id,
                    "description": child["description"],
                    "system_prompt": child.get("system_prompt", ""),
                    "user_prompt_template": child.get("user_prompt_template", ""),
                    "post_process_template": child.get("post_process_template"),
                    "model": child.get("model", "anthropic/claude-sonnet-4-20250514"),
                    "fallback_model": child.get("fallback_model"),
                    "max_tokens": child.get("max_tokens", 4096),
                    "temperature": child.get("temperature", 0.7),
                    "version": 1,
                    "is_active": True,
                }
                if "children" in child:
                    yield from flatten_children(child["children"], skill_id)

        from storyloom.memory.models.skill import Skill

        for item in flatten_children(data.get("categories", [])):
            await self._store.create_skill(Skill(**item))

        await self.load_from_db()

    def format_tree(self, indent: str = "  ") -> str:
        """Format skill tree for embedding in LLM prompts."""
        lines = []

        def walk(nodes, depth=0):
            for node in nodes:
                prefix = indent * depth
                if "children" in node and node["children"]:
                    emoji = {"writing": "📝", "review": "🔍", "research": "📖"}.get(
                        node.get("category", ""), "•"
                    )
                    lines.append(f"{prefix}{emoji} {node['name']}")
                    walk(node["children"], depth + 1)
                else:
                    desc = node.get("description", "").split(".")[0][:60]
                    lines.append(f"{prefix}  {node['name']} — {desc}")

        walk(self._tree)
        return "\n".join(lines)
