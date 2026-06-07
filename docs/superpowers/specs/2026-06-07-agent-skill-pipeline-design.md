# LLM-Driven Agent Skill Pipeline — Design Spec

## Overview

Replace the current hardcoded stage pipeline (`Planner → Writer → Editor → Continuity → QualityGate`) with an LLM-driven supervisor agent that autonomously orchestrates chapter generation by selecting from a set of declaratively defined skills.

The core shift: **code registers what skills are available; the LLM decides when and in what order to use them.**

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     Pipeline Supervisor                          │
│  ┌──────────────┐   ┌──────────────────┐   ┌──────────────────┐ │
│  │  Context      │   │   Decision Loop   │   │  Skill Engine    │ │
│  │  Manager      │──▶│                   │──▶│                  │ │
│  │               │   │  ① LLM 分析状态   │   │  ① 渲染模板      │ │
│  │  3 层上下文:  │   │  ② LLM 选 Skill   │   │  ② 调 LiteLLM   │ │
│  │  L1: 不变信息 │   │  ③ 代码执行       │   │  ③ 后处理        │ │
│  │  L2: 累积状态 │   │  ④ 评估 → 循环    │   │  ④ 记录日志      │ │
│  │  L3: 临时信息 │   └──────────────────┘   └──────────────────┘ │
│  └──────────────┘                                                │
│                         │                                         │
│                         ▼                                        │
│                   ┌──────────────────────┐                       │
│                   │    Skill Registry     │                       │
│                   │  DB → 运行时缓存       │                       │
│                   │  支持热重载            │                       │
│                   └──────────────────────┘                       │
└──────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Storage Layer                              │
│  ┌───────────┐  ┌───────────────┐  ┌───────────┐                │
│  │   skills   │  │ skill_versions│  │ skill_runs│                │
│  │   (当前)   │  │   (历史)      │  │   (日志)  │                │
│  └───────────┘  └───────────────┘  └───────────┘                │
└──────────────────────────────────────────────────────────────────┘
```

## Data Model

### Skills Table

```sql
CREATE TABLE skills (
    id          TEXT PRIMARY KEY,
    category    TEXT NOT NULL,          -- writing / review / research / management
    name        TEXT NOT NULL UNIQUE,
    parent_id   TEXT REFERENCES skills(id),
    description TEXT NOT NULL,          -- LLM 据此决定何时调用
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT NOT NULL,  -- Jinja2 模板, 渲染上下文
    post_process_template TEXT,          -- 可选, 输出后处理
    model       TEXT NOT NULL DEFAULT 'anthropic/claude-sonnet-4-20250514',
    fallback_model TEXT,                 -- 主模型失败时的备选
    max_tokens  INTEGER NOT NULL DEFAULT 4096,
    temperature REAL NOT NULL DEFAULT 0.7,
    version     INTEGER NOT NULL DEFAULT 1,
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skill_versions (
    id          TEXT PRIMARY KEY,
    skill_id    TEXT NOT NULL REFERENCES skills(id),
    version     INTEGER NOT NULL,
    description TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT NOT NULL,
    post_process_template TEXT,
    model       TEXT NOT NULL,
    max_tokens  INTEGER NOT NULL,
    temperature REAL NOT NULL,
    change_note TEXT NOT NULL DEFAULT '',
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by  TEXT NOT NULL DEFAULT 'system'
);

CREATE TABLE skill_runs (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL,
    chapter_number  INTEGER NOT NULL,
    step_number     INTEGER NOT NULL,       -- 在第几步调用的
    skill_id        TEXT NOT NULL REFERENCES skills(id),
    llm_decision    TEXT,                    -- LLM 选这个 skill 的 rationale
    input_preview   TEXT,
    output_preview  TEXT,
    tokens_in       INTEGER DEFAULT 0,
    tokens_out      INTEGER DEFAULT 0,
    latency_ms      INTEGER DEFAULT 0,
    cost_usd        REAL DEFAULT 0,
    status          TEXT DEFAULT 'success',  -- success / failed / skipped
    error_message   TEXT,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_skill_runs_project ON skill_runs(project_id, chapter_number);
```

### PipelineContext Data Structure

```python
class PipelineContext(BaseModel):
    # Layer 1: Immutable (entire novel)
    project_id: str
    story_bible: StoryBible
    character_cards: list[CharacterCard]
    world_state: WorldState
    chapter_history: list[ChapterSummary]
    style_guide: str | None

    # Layer 2: Accumulating (current chapter)
    chapter_number: int
    chapter_content: str | None
    current_outline: str | None
    quality_report: dict | None

    # Layer 3: Ephemeral (single skill execution)
    supervisor_instructions: str | None
    revision_focus: list[str] | None

    # Execution log (appended)
    skill_log: list[SkillRunLog] = []
```

### SkillDef (Runtime Representation)

```python
@dataclass
class SkillDef:
    id: str
    category: str
    name: str
    description: str
    system_prompt: str
    user_prompt_template: str
    post_process_template: str | None
    model: str
    fallback_model: str | None
    max_tokens: int
    temperature: float

@dataclass
class SkillGroup:
    name: str
    description: str
    children: list[SkillGroup | SkillDef]  # N-level nesting
```

### SkillRunLog

```python
class SkillRunLog(BaseModel):
    step: int
    skill_name: str
    rationale: str
    content_preview: str
    tokens_used: int
    cost_usd: float
    status: str  # success / failed
```

## Pipeline Supervisor (Decision Loop)

### Process

```
for step in range(max_steps=20):
    1. LLM examines context (current draft + recent skill_log)
    2. LLM chooses ONE skill via function calling
    3. Code executes the chosen skill
    4. Result updates shared context
    5. If decision == "chapter_complete" → break
```

### Supervisor System Prompt

```
You are the writing supervisor for a novel generation pipeline.
Your job is to orchestrate chapter creation by delegating to specialist skills.
Think of yourself as an editor-in-chief.

## Decision Process
Each turn, review the current state and call ONE skill.
After the skill returns, evaluate the result. Repeat until the chapter is done.

## Completion Criteria
Call chapter_complete only when ALL of:
1. Full chapter content exists
2. Prose has been edited
3. No continuity issues
4. Quality assessment passes all dimensions

## Available Skills
(Skills are registered as function tools — call them by name.)
```

### Dynamic Tool Registration

Each SkillDef is compiled into a function tool at runtime. The tool descriptors are built from DB data, not hardcoded:

```python
def build_tools(registry: SkillRegistry):
    tools = []
    for skill in registry.list_active():
        tools.append({
            "type": "function",
            "function": {
                "name": skill.name,
                "description": skill.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rationale": {"type": "string", "description": "Why this skill now"},
                        "instructions": {"type": "string", "description": "Specific guidance"},
                    },
                    "required": ["rationale"],
                },
            },
        })
    tools.append(CHAPTER_COMPLETE_TOOL)
    return tools
```

### Skill Execution Engine

Fully generic — no per-skill logic:

```python
class SkillExecutionEngine:
    async def execute(self, skill: SkillDef, context: PipelineContext) -> SkillOutput:
        messages = [
            {"role": "system", "content": skill.system_prompt},
            {"role": "user", "content": Template(skill.user_prompt_template).render(
                **context.model_dump(),
                supervisor_instructions=context.supervisor_instructions,
            )},
        ]
        response = await complete(
            messages=messages,
            model=skill.model,
            max_tokens=skill.max_tokens,
            temperature=skill.temperature,
        )
        content = response.content
        if skill.post_process_template:
            content = Template(skill.post_process_template).render(
                original_content=context.chapter_content,
                new_content=content,
            )
        await self._log_skill_run(skill, context, response)
        return SkillOutput(content=content, ...)
```

## Context Flow

```
 Decision Loop Iteration
 ┌─────────────────────────────────────┐
 │ 1. Render context for LLM decision  │
 │    - Current draft (truncated)      │
 │    - Last 5 skill_log entries       │
 │    - Historical patterns            │
 └──────────────┬──────────────────────┘
                ▼
 ┌─────────────────────────────────────┐
 │ 2. LLM calls skill (function tool)  │
 └──────────────┬──────────────────────┘
                ▼
 ┌─────────────────────────────────────┐
 │ 3. Execute skill                    │
 │    - Update chapter_content         │
 │    - Update quality_report          │
 │    - Append to skill_log            │
 └──────────────┬──────────────────────┘
                ▼
 ┌─────────────────────────────────────┐
 │ 4. LLM evaluates result             │
 │    → loop or chapter_complete       │
 └─────────────────────────────────────┘
```

Storage rules:
- **L1** (Bible, history, world state): loaded once at pipeline start
- **L2** (chapter content, outline): updated after each skill execution
- **L3** (instructions, focus): reset to None each iteration
- **skill_log**: appended, capped to last 5 entries in prompt

## Historical Feedback Loop

Supervisor prompt includes historical patterns from `skill_runs` to guide decisions:

```
### Historical Skill Usage (this project)
  - writer: used 7x, avg 2450 tokens
  - editor: used 3x, avg 1200 tokens
  - planner: used 2x, avg 890 tokens

### Previous Chapter Pattern
Chapter 2: planner → writer → editor → continuity → writer(revision) → quality → done
```

This data is queried at pipeline start and injected into the supervisor prompt.

## Error Handling & Guardrails

| Scenario | Guard |
|----------|-------|
| Infinite loop | `max_steps=20`, `max_cost=$0.50` |
| LLM picks same skill 3x in a row | Inject warning into prompt, force direction change |
| Context overflow | Truncate skill_log to last 5, truncate chapter_content to 2000 chars |
| Skill execution failure | Try fallback_model if defined; return error to supervisor |
| All skills fail | Force `chapter_complete(status="partial")` |

## Skill Management API

```
GET    /api/skills                 → 分类树
GET    /api/skills/:id            → 详情 + 版本历史
PUT    /api/skills/:id            → 更新（自动创建新版本）
POST   /api/skills/:id/rollback   → 回退到指定版本
POST   /api/skills/preview        → 用临时 prompt 跑预览（不保存）
GET    /api/skills/runs           → 某章节的执行流水
GET    /api/skills/analysis       → 技能使用效率分析
```

## Migration Plan

### Phase 1: Data Layer
- Add migration for `skills`, `skill_versions`, `skill_runs` tables
- Add pydantic models for all three
- Seed initial skills from definitions.yaml
- Add CRUD API routes

### Phase 2: Execution Engine
- Build `SkillExecutionEngine` (generic, template-driven)
- Build `SkillRegistry` (DB-backed, hot-reloadable)
- No pipeline changes yet — can test individual skills via API

### Phase 3: Supervisor Loop
- Build `SupervisorPipeline` with decision loop
- Build function calling tool registration
- Add toggle in PipelineOrchestrator

### Phase 4: Frontend
- SkillEditor.vue: list, edit, preview, compare versions
- PipelineRun visualization: show skill_log as waterfall

### Phase 5: Cutover
- Run comparative tests (old vs new)
- Default to new pipeline
- Deprecate old hardcoded stage code

## Trade-offs & Rationale

| Decision | Rationale |
|----------|-----------|
| DB storage for skills | Enables user-facing editor, versioning, hot-reload; skills change more often than code |
| Jinja2 for templates | Existing dependency, familiar, safe sandboxed rendering |
| Function calling for skill selection | Structured output, native LLM support, easy to log and audit |
| Supervisor+executor separation | Clean boundary: LLM decides WHAT, code decides HOW |
| 3-layer context | Prevents context pollution between iterations while preserving history |
| skill_log capped at 5 | Bounded token consumption per iteration |
