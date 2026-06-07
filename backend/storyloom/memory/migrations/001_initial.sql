CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT DEFAULT '',
    personality TEXT DEFAULT '',
    appearance TEXT DEFAULT '',
    background TEXT DEFAULT '',
    location TEXT DEFAULT '',
    status TEXT DEFAULT 'active',
    emotional_arc TEXT DEFAULT '',
    last_seen_chapter INTEGER,
    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, name)
);

CREATE TABLE IF NOT EXISTS plot_threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    first_chapter INTEGER,
    target_chapter INTEGER,
    last_seen_chapter INTEGER,
    description TEXT DEFAULT '',
    UNIQUE(project_id, name)
);

CREATE TABLE IF NOT EXISTS world_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    chapter_number INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, key)
);

CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    number INTEGER NOT NULL,
    title TEXT DEFAULT '',
    status TEXT DEFAULT 'planned',
    word_count INTEGER DEFAULT 0,
    summary TEXT DEFAULT '',
    outline TEXT DEFAULT '',
    draft_path TEXT,
    UNIQUE(project_id, number)
);

CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    pipeline_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    model TEXT,
    tokens_in INTEGER DEFAULT 0,
    tokens_out INTEGER DEFAULT 0,
    latency_ms INTEGER DEFAULT 0,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
