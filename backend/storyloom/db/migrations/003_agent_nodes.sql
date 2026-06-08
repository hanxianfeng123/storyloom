CREATE TABLE IF NOT EXISTS agent_trees (
    project_id TEXT PRIMARY KEY,
    tree_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS agent_nodes (
    id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    node_type TEXT NOT NULL DEFAULT 'agent',
    parent_id TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    system_prompt TEXT NOT NULL DEFAULT '',
    llm_model TEXT,
    temperature REAL NOT NULL DEFAULT 0.7,
    max_tokens INTEGER NOT NULL DEFAULT 4096,
    interests TEXT NOT NULL DEFAULT '[]',
    pool_size INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (project_id, id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
