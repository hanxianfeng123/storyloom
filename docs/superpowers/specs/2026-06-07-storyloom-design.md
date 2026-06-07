# Storyloom: AI Novel Generation Platform

> **Status:** Design Draft
> **Date:** 2026-06-07
> **Author:** storyloom team

---

## 1. Project Overview

Storyloom is an open-source AI novel generation platform. It orchestrates multi-LLM pipelines to plan, write, edit, and quality-check novel chapters, then publish them to web/audio/video outputs through pluggable adapters.

### Core Principles

- **Pipeline as workflow** — Novel generation is a multi-stage software engineering problem, not a single prompt completion.
- **Multi-provider LLM** — Different tasks and languages benefit from different models; the platform routes intelligently.
- **Persistent memory** — Novel-length context exceeds any LLM window; structured external memory is foundational.
- **Human in the loop** — Review gates at key stages ensure quality without blocking flow.
- **Bilingual from day one** — Chinese and English as first-class citizens, with language-aware routing and prompt templates.

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌────────────────────────────────────────────────────────────┐
│  Frontend (Vue + Vite SPA)                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │ Pipeline  │ │ Memory   │ │ Output   │ │ Project      │ │
│  │ Dashboard │ │ Explorer │ │ Preview  │ │ Settings     │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘ │
└──────────────────────┬─────────────────────────────────────┘
                       │ REST API + WebSocket
                       ▼
┌────────────────────────────────────────────────────────────┐
│  Backend (Python FastAPI)                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Pipeline Orchestrator                             │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │    │
│  │  │Planner  │ │ Writer  │ │ Editor  │ │Continuity│  │    │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬─────┘  │    │
│  │       │           │           │           │         │    │
│  │       ▼           ▼           ▼           ▼         │    │
│  │  ┌──────────────────────────────────────────────┐   │    │
│  │  │          Quality Gate                        │   │    │
│  │  │  ┌─────────────────┐  ┌───────────────────┐ │   │    │
│  │  │  │ Deterministic    │  │ LLM Review        │ │   │    │
│  │  │  │ Checks (free)    │  │ (5-dimension)     │ │   │    │
│  │  │  └─────────────────┘  └───────────────────┘ │   │    │
│  │  └──────────────────────────────────────────────┘   │    │
│  └────────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │  Providers   │  │  Memory Layer  │  │  Output        │  │
│  │  ┌──────────┐│  │  ┌──────────┐  │  │  ┌──────────┐  │  │
│  │  │ OpenAI   ││  │  │ SQLite   │  │  │  │Filesystem│  │  │
│  │  │ Anthropic││  │  │sqlite-vec│  │  │  │          │  │  │
│  │  │ DeepSeek ││  │  │Migrations│  │  │  └──────────┘  │  │
│  │  │ Ollama   ││  │  └──────────┘  │  └────────────────┘  │
│  │  └──────────┘│  └────────────────┘                       │
│  └──────────────┘                                           │
│  ┌──────────────┐  ┌────────────────┐                       │
│  │  CLI         │  │  i18n          │                       │
│  │  init | serve│  │  zh/  en/      │                       │
│  └──────────────┘  └────────────────┘                       │
└────────────────────────────────────────────────────────────┘
```

### 2.2 Project Structure

```
storyloom/
├── backend/
│   └── storyloom/
│       ├── __init__.py
│       ├── main.py                     # FastAPI app entry
│       │
│       ├── core/                       # Core pipeline engine
│       │   ├── __init__.py
│       │   ├── pipeline.py             # Orchestrator: stage sequencing, routing, retry
│       │   ├── contract.py             # StageInput, StageOutput, PipelineContext
│       │   ├── stages/
│       │   │   ├── __init__.py
│       │   │   ├── base.py             # Stage ABC
│       │   │   ├── planner.py
│       │   │   ├── writer.py
│       │   │   ├── editor.py
│       │   │   ├── continuity.py       # Cross-chapter consistency
│       │   │   └── quality_gate.py     # Deterministic + LLM checks
│       │   ├── task_queue.py           # Background task execution
│       │   ├── errors.py               # LLM retry, stage error hierarchy
│       │   ├── cache.py                # LLM response cache
│       │   └── logging.py              # Structured logging (structlog)
│       │
│       ├── providers/                  # LLM provider abstraction
│       │   ├── __init__.py
│       │   ├── base.py                 # Protocol/abstract interface
│       │   ├── openai.py
│       │   ├── anthropic.py
│       │   ├── deepseek.py
│       │   ├── ollama.py
│       │   ├── router.py               # Language + task-aware model routing
│       │   └── errors.py               # Provider-specific error mapping
│       │
│       ├── memory/                     # Persistent memory layer
│       │   ├── __init__.py
│       │   ├── store.py                # SQLite CRUD
│       │   ├── vector.py               # sqlite-vec vector search
│       │   ├── models/                 # Pydantic models for memory entities
│       │   │   ├── character.py
│       │   │   ├── plot_thread.py
│       │   │   ├── world_state.py
│       │   │   └── chapter.py
│       │   └── migrations/             # SQLite schema migrations
│       │
│       ├── output/                     # Output adapters
│       │   ├── __init__.py
│       │   ├── base.py                 # Output adapter interface
│       │   ├── filesystem.py           # Serialize to .md + organize on disk
│       │   └── web/                    # Web publishing adapter (v1)
│       │       ├── __init__.py
│       │       └── publisher.py
│       │
│       ├── i18n/                       # Bilingual support
│       │   ├── __init__.py
│       │   ├── zh/
│       │   │   ├── prompts/            # Chinese prompt templates
│       │   │   └── strings.py          # UI strings
│       │   └── en/
│       │       ├── prompts/            # English prompt templates
│       │       └── strings.py
│       │
│       ├── cli/                        # Command-line interface
│       │   ├── __init__.py
│       │   ├── main.py                 # Click/Typer entry point
│       │   └── commands/
│       │       ├── init.py             # storyloom init
│       │       ├── serve.py            # storyloom serve
│       │       └── run.py              # storyloom run (headless pipeline)
│       │
│       ├── api/                        # FastAPI routes
│       │   ├── __init__.py
│       │   ├── deps.py                 # Dependency injection
│       │   ├── routes/
│       │   │   ├── projects.py
│       │   │   ├── chapters.py
│       │   │   ├── pipeline.py         # Start/stop/status
│       │   │   ├── memory.py           # Character/plot/world exploration
│       │   │   └── output.py           # Publish endpoints
│       │   └── ws.py                   # WebSocket: pipeline progress, logs
│       │
│       └── config/                     # Configuration management
│           ├── __init__.py
│           ├── settings.py             # Pydantic settings
│           └── pipeline.yaml           # Pipeline stage definitions
│
├── frontend/                           # Vue + Vite SPA
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── router/
│   │   ├── pages/
│   │   │   ├── ProjectList.vue
│   │   │   ├── ProjectDetail.vue
│   │   │   ├── PipelineRun.vue        # Pipeline dashboard
│   │   │   ├── MemoryExplorer.vue      # Character/plot/world browser
│   │   │   └── Settings.vue
│   │   ├── components/
│   │   │   ├── StageCard.vue           # Single stage visualization
│   │   │   ├── ReviewGate.vue          # Approval dialog
│   │   │   ├── ChapterDiff.vue         # Before/after editor diff
│   │   │   └── MemoryTree.vue          # Memory explorer tree
│   │   ├── api/                        # API client
│   │   ├── stores/                     # Pinia state management
│   │   └── locales/                    # Frontend i18n
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── tests/
│   ├── unit/
│   │   ├── test_planner.py
│   │   ├── test_writer.py
│   │   ├── test_editor.py
│   │   └── test_quality_gate.py
│   ├── integration/
│   │   ├── test_pipeline.py            # Full pipeline run with mock LLM
│   │   └── test_memory.py
│   └── fixtures/
│       ├── sample_project/
│       └── mock_llm_responses/
│
├── docs/
│   ├── guide/
│   │   ├── quickstart.md
│   │   ├── configuration.md
│   │   └── pipeline-customization.md
│   ├── api/
│   │   └── openapi.json
│   └── contributor/
│       ├── CONTRIBUTING.md
│       └── CODE_OF_CONDUCT.md
│
├── examples/
│   └── quickstart-novel/               # Ready-to-run example project
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                      # Run tests on PR
│   │   └── release.yml                 # PyPI publish
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── Makefile                            # dev, test, lint, build
├── pyproject.toml                      # Python project config
├── docker-compose.yml                  # Backend + frontend for dev
├── LICENSE
└── README.md
```

---

## 3. Core Pipeline Design

### 3.1 Stage Contract

```python
# core/contract.py

class StageInput(BaseModel):
    project_id: str
    chapter_id: str | None
    context: PipelineContext

class PipelineContext(BaseModel):
    story_bible: StoryBible
    character_cards: list[CharacterCard]
    world_state: WorldState
    chapter_history: list[ChapterSummary]
    style_guide: str | None = None

class StageOutput(BaseModel):
    content: str | None
    partial: bool = False                # True if LLM timed out mid-generation
    metrics: StageMetrics                # tokens, latency, model
    decision: Literal["approved", "rejected", "need_revision"]
    revise_target: Literal["writer", "editor"] | None = None
    revision_context: dict | None = None # structured failure reasons
    review_notes: str | None = None

class StageMetrics(BaseModel):
    model: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    cost_usd: float
```

### 3.2 Stage Definitions

| Stage | Input | Output | Model | Key Behavior |
|-------|-------|--------|-------|-------------|
| **Planner** | Bible, characters, world state, previous chapter summary | Chapter outline (3-5 sections) + word count target | Claude Sonnet | Review gate: `optional`; user can approve/modify/reject |
| **Writer** | Outline + context + style guide | Full chapter markdown | Per-language route | Word count governed; `partial=True` on timeout |
| **Editor** | Draft chapter | Revised chapter + change log | Claude Sonnet | Light polish; preserves original for diff view |
| **Continuity** | Current + last 3 chapters | Consistency report: flagged discrepancies | Claude Sonnet (cheap model) | Non-blocking; flags feed into Quality Gate |
| **Quality Gate** | Edited chapter + continuity report | Pass/fail + issue list | Deterministic + Claude Sonnet | Deterministic checks first (free); LLM review (5 dimensions) only on pass |

### 3.3 Pipeline Orchestrator

```python
# core/pipeline.py

class PipelineOrchestrator:
    """
    Sequences stages, manages state, routes revisions, handles cancellation.
    
    Pipeline lifecycle:
    queued → running → [stage loop...] → completed | failed | cancelled
    
    Revision routing:
    - Quality Gate rejects with structural issue → revise_target="writer"
    - Quality Gate rejects with prose issue → revise_target="editor"
    - Max 2 revision loops per chapter, then forced pass with warning.
    """
    
    stages: list[Stage]           # From config
    review_gates: ReviewGateConfig
    trust_mode: bool              # Auto-approve after N consecutive passes
    cancel_event: asyncio.Event   # User cancellation
    
    async def run(self, project_id: str, chapter_id: str | None = None) -> PipelineResult:
        ...
```

### 3.4 Review Gate Configuration

```yaml
# config/pipeline.yaml
review_gates:
  planner: optional       # Pause after planner for user review
  writer: skip            # Auto-continue
  editor: optional        # Pause if user wants to review edits
  continuity: skip        # Auto-continue (non-blocking)
  quality: always         # Always show results (blocking on critical only)

trust_mode:
  enabled: true
  auto_approve_after: 5   # After 5 consecutive passes, skip optional gates
```

### 3.5 Error Handling

```
Retry:  LLM call fails → exponential backoff (1s, 2s, 4s) × 3 attempts
Timeout: Stage exceeds deadline → StageOutput(partial=True, content=<partial>)
Cancel:  User sends cancel → asyncio.Event → stages check and exit
Fail:    Stage fails after retries → pipeline status=failed, user notified
```

---

## 4. Provider Abstraction Layer

### 4.1 Interface

```python
# providers/base.py

class LLMProvider(Protocol):
    """Minimal Protocol: one method, typed."""
    
    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        ...

class LLMResponse(BaseModel):
    content: str
    model: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
```

### 4.2 Router Logic

```python
# providers/router.py

# Routing matrix — configurable via settings
ROUTING_TABLE = {
    ("planner", "zh"):   ("claude-sonnet", "anthropic"),
    ("planner", "en"):   ("claude-sonnet", "anthropic"),
    ("writer", "zh"):    ("deepseek-chat", "deepseek"),
    ("writer", "en"):    ("claude-sonnet", "anthropic"),
    ("editor", "zh"):    ("claude-sonnet", "anthropic"),
    ("editor", "en"):    ("claude-sonnet", "anthropic"),
    ("quality", "zh"):   ("claude-sonnet", "anthropic"),
    ("quality", "en"):   ("claude-sonnet", "anthropic"),
}
```

---

## 5. Memory Layer

### 5.1 Storage

- **SQLite** (`store.py`): Character state, plot thread status, chapter metadata, world state, operation logs
- **sqlite-vec** (`vector.py`): Semantic search over past chapters for context injection
- **Migrations** (`migrations/`): Raw SQL files numbered sequentially, applied on startup

### 5.2 Key Entities

| Entity | Fields | Purpose |
|--------|--------|---------|
| `Character` | name, status, location, relationships, emotional_arc | Track character state across chapters |
| `PlotThread` | name, status, first_chapter, target_chapter, last_seen | Dormant thread detection |
| `Chapter` | number, title, word_count, summary, status | Chapter lifecycle tracking |
| `WorldState` | key, value, updated_at | Setting consistency (e.g., "当前季节: 深秋") |
| `OperationLog` | pipeline_id, stage, model, tokens, latency, result | Full audit trail |

### 5.3 Context Injection

Before each stage execution, the orchestrator queries:

1. Current character states (from `store`)
2. Active plot threads (from `store`)
3. Last 3 chapter summaries (from `store`)
4. Relevant past content via vector search (from `vector`)
5. World state (from `store`)

Assembled into `PipelineContext` and passed to the stage.

---

## 6. Quality Gate Design

### 6.1 Deterministic Checks (Free)

| Check | Severity | Target |
|-------|----------|--------|
| Dormant thread (>3 chapters unseen) | warning | Plot thread management |
| Absent main character (>5 chapters) | warning | Character presence |
| Word count deviation (>20% from target) | info | Length governance |
| Unresolved foreshadowing | warning | Plot integrity |

### 6.2 LLM Review (5 Dimensions, v1)

| Dimension | What It Assesses |
|-----------|-----------------|
| Plot consistency | Does this chapter logically follow from previous? |
| Character voice | Do characters act/speak consistently? |
| Prose quality | Sentence flow, repetition, readability |
| Pacing | Is the chapter too slow/too rushed for its content? |
| Language accuracy | Grammar, idiom correctness (language-aware) |

Each dimension scored: **pass / flag / fail**. Any `fail` → `revise_target=writer` or `editor`. Two consecutive failures with no improvement → forced pass with logged warning.

---

## 7. Output Layer

### 7.1 Filesystem Serialization

```
works/{project_name}/
├── bible/                     # Read from memory layer
│   ├── characters.yaml
│   ├── world.yaml
│   └── plot-threads.yaml
├── outline.yaml               # Generated by Planner
├── chapters/
│   ├── ch-001/
│   │   ├── draft.md           # Writer output
│   │   ├── edited.md          # Editor output
│   │   ├── continuity.md      # Continuity report
│   │   └── quality.md         # Quality gate result
│   └── ch-002/
├── published/                 # Output adapter targets
│   ├── web/                   # Web publisher output
│   ├── audio/                 # TTS (v2)
│   └── video/                 # Video (v3)
└── .storyloom/                # Internal state
```

### 7.2 CLI Commands

```bash
storyloom init my-novel              # Create project scaffolding
storyloom serve                      # Start web UI
storyloom run --chapter 3            # Headless: generate one chapter
storyloom run --chapter 3-5          # Headless: generate chapters 3-5
storyloom publish web                # Publish to web
```

---

## 8. Tech Stack Summary

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Backend framework | FastAPI | Async, WebSocket built-in, Pydantic validation |
| LLM providers | OpenAPI-compatible + Anthropic SDK | Router handles selection |
| Database | SQLite + sqlite-vec | Zero ops, transactional consistency, sufficient for v1 |
| Frontend | Vue 3 + Vite + Pinia | SPA, no SSR needed, TypeScript |
| Logging | structlog | Structured logging with minimal code |
| CLI | Typer (built on Click) | Modern Python CLI, async support |
| Task queue | in-process asyncio | Simple for v1; swap for Celery/ARQ later if needed |
| Testing | pytest + pytest-asyncio | Standard Python testing |
| CI | GitHub Actions | pytest on PR, release on tag |

---

## 9. Architecture Decision Records

### ADR-001: SQLite + sqlite-vec for Memory Layer

- **Status:** Accepted
- **Context:** Need persistent structured memory + vector search for context injection. Must work offline, zero ops.
- **Decision:** SQLite for structured data, sqlite-vec extension for vector search. Single file, transactional consistency, no external service.
- **Consequences:** Good for v1 scale (thousands of vectors per novel). Migration to LanceDB possible if scale demands, via abstracted `memory/vector.py` interface.

### ADR-002: FastAPI for Backend Framework

- **Status:** Accepted
- **Context:** Need async I/O for concurrent LLM calls, WebSocket for pipeline progress streaming, Pydantic for contract validation.
- **Decision:** FastAPI provides all three natively.
- **Consequences:** Single Python process for v1. Background LLM calls handled via asyncio tasks.

### ADR-003: Provider Abstraction via Protocol

- **Status:** Accepted
- **Context:** Different LLMs excel at different tasks/languages. Need to route without coupling to any single provider.
- **Decision:** Minimal `LLMProvider` Protocol (one `complete()` method). Providers implement it. Router selects by task + language.
- **Consequences:** New providers = one file + one routing entry. No dependency on any single provider SDK.

### ADR-004: Synchronous Serial Pipeline

- **Status:** Accepted
- **Context:** Novel generation is fundamentally sequential (Plan → Write → Edit → Review). Parallelism adds inconsistency.
- **Decision:** v1 runs stages serially in-process. Parallel execution can be added later for independent tasks (e.g., simultaneous Editor + Continuity).
- **Consequences:** Simple orchestration, easy debugging. Longer per-chapter latency, but acceptable for async writing workflow.

### ADR-005: Vue + Vite SPA (No SSR)

- **Status:** Accepted
- **Context:** Storyloom is a login-required authoring tool, not a content site. SEO irrelevant. SSR adds deployment complexity.
- **Decision:** Vue 3 SPA built with Vite. API calls to FastAPI backend. WebSocket for real-time updates.
- **Consequences:** Simple deployment (build static files, serve via Nginx or FastAPI). No Node.js server needed at runtime.

---

## 10. Open Source Scaffolding

| Asset | Purpose |
|-------|---------|
| MIT License | Permissive, community-friendly |
| CONTRIBUTING.md | PR workflow, dev setup, coding standards |
| CODE_OF_CONDUCT.md | Contributor expectations |
| Issue/PR templates | Structured bug reports and feature requests |
| GitHub Actions CI | pytest on push/PR + release to PyPI |
| Makefile | `make dev`, `make test`, `make lint`, `make build` |
| docker-compose.yml | One-command dev environment (backend + frontend) |
| README.md | Project overview, quick start, architecture summary |
| `examples/quickstart-novel/` | Ready-to-run example project |

---

## 11. v1 Scope Boundaries

### In Scope (v1)

- Core pipeline: Planner → Writer → Editor → Continuity → Quality Gate → Output
- Multi-provider LLM support (OpenAI, Anthropic, DeepSeek, Ollama)
- Bilingual prompt templates (Chinese + English)
- SQLite + sqlite-vec memory layer
- Filesystem output + Web publishing adapter
- CLI: `init`, `serve`, `run`
- Vue 3 SPA frontend
- Review gates with trust mode
- Structured logging + pipeline execution history
- Docker Compose dev environment

### Out of Scope (v1, deferred to v2+)

- TTS/audio output adapter
- Video output adapter
- Desktop shell (Electron/Tauri)
- Plugin/extension system for community stages
- Asynchronous/event-driven pipeline execution
- Dedicated vector database (LanceDB/Qdrant)
- Prometheus/Grafana metrics
- Kubernetes deployment

---

## 12. Spec Self-Review Checklist

- [x] No TBD or TODO placeholders
- [x] Architecture matches feature descriptions
- [x] Scope is focused for a single implementation plan
- [x] No ambiguous requirements — all design decisions are explicit
- [x] All key interfaces (Stage, Provider, PipelineContext) are typed
- [x] Versioning/evolution path documented (v1 boundaries, v2 deferrals)
- [x] Error handling, cancellation, partial output covered
- [x] Open-source scaffolding items listed with purpose
- [x] ADRs document the 5 key decisions with rationale
