"""backend/storyloom/db/agent_repo.py"""
from pathlib import Path

import aiosqlite

from storyloom.swarm.models import AgentNode


class AgentRepo:
    """Persist and load agent trees from SQLite."""

    def __init__(self, db_url: str):
        self._db_url = db_url
        self._conn: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        """Ensure tables exist by running the migration."""
        self._conn = await aiosqlite.connect(self._db_url)
        self._conn.row_factory = aiosqlite.Row
        mig_path = Path(__file__).parent / "migrations" / "003_agent_nodes.sql"
        sql = mig_path.read_text()
        await self._conn.executescript(sql)
        await self._conn.commit()

    async def save_tree(self, project_id: str, root: AgentNode) -> None:
        """Serialize entire tree to JSON blob."""
        if self._conn is None:
            raise RuntimeError("AgentRepo not initialized")
        await self._conn.execute(
            """INSERT OR REPLACE INTO agent_trees (project_id, tree_json, updated_at)
               VALUES (?, ?, datetime('now'))""",
            (project_id, root.model_dump_json()),
        )
        await self._conn.commit()

    async def load_tree(self, project_id: str) -> AgentNode | None:
        """Deserialize tree from JSON blob."""
        if self._conn is None:
            raise RuntimeError("AgentRepo not initialized")
        cursor = await self._conn.execute(
            "SELECT tree_json FROM agent_trees WHERE project_id = ?",
            (project_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return AgentNode.model_validate_json(row["tree_json"])

    async def update_node(
        self, project_id: str, node_id: str, updates: dict
    ) -> None:
        """Load tree, update a node, save back."""
        tree = await self.load_tree(project_id)
        if tree is None:
            raise ValueError(f"Tree not found for project {project_id}")
        node = tree.find(node_id)
        if node is None:
            raise ValueError(f"Node {node_id} not found in project {project_id}")
        for key, value in updates.items():
            setattr(node, key, value)
        await self.save_tree(project_id, tree)

    async def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            await self._conn.close()
            self._conn = None
