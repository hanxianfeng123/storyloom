CREATE TABLE IF NOT EXISTS skills (
    id          TEXT PRIMARY KEY,
    category    TEXT NOT NULL,
    name        TEXT NOT NULL UNIQUE,
    parent_id   TEXT REFERENCES skills(id),
    description TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT NOT NULL DEFAULT '',
    post_process_template TEXT,
    model       TEXT NOT NULL DEFAULT 'anthropic/claude-sonnet-4-20250514',
    fallback_model TEXT,
    max_tokens  INTEGER NOT NULL DEFAULT 4096,
    temperature REAL NOT NULL DEFAULT 0.7,
    version     INTEGER NOT NULL DEFAULT 1,
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skill_versions (
    id          TEXT PRIMARY KEY,
    skill_id    TEXT NOT NULL REFERENCES skills(id),
    version     INTEGER NOT NULL,
    description TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT NOT NULL DEFAULT '',
    post_process_template TEXT,
    model       TEXT NOT NULL,
    max_tokens  INTEGER NOT NULL,
    temperature REAL NOT NULL,
    change_note TEXT NOT NULL DEFAULT '',
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by  TEXT NOT NULL DEFAULT 'system'
);

CREATE TABLE IF NOT EXISTS skill_runs (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL,
    chapter_number  INTEGER NOT NULL,
    step_number     INTEGER NOT NULL,
    skill_id        TEXT NOT NULL REFERENCES skills(id),
    llm_decision    TEXT,
    input_preview   TEXT,
    output_preview  TEXT,
    tokens_in       INTEGER DEFAULT 0,
    tokens_out      INTEGER DEFAULT 0,
    latency_ms      INTEGER DEFAULT 0,
    cost_usd        REAL DEFAULT 0,
    status          TEXT DEFAULT 'success',
    error_message   TEXT,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_skill_runs_project ON skill_runs(project_id, chapter_number);
CREATE INDEX IF NOT EXISTS idx_skills_parent ON skills(parent_id);
