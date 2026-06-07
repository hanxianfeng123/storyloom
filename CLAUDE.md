# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install all dependencies
make install                          # backend + frontend

# Development (run both in separate terminals)
make backend-dev                      # uvicorn :8000
make frontend-dev                     # vite :5173 (proxies /api to :8000)

# Test & lint
make test                             # pytest -v (backend)
make lint                             # ruff check (backend)

# Single backend test
cd backend && pytest -v tests/unit/test_pipeline.py -k test_name

# Frontend build
cd frontend && npm run build

# Docker
docker compose build
docker compose up -d
```

## Architecture

**storyloom** is an AI novel generation platform. Vue 3 + TS frontend, Python backend.

### Directory Layout

| Path | Purpose |
|------|---------|
| `backend/storyloom/` | Python backend package |
| `backend/storyloom/core/contract.py` | All Pydantic models: `PipelineContext`, `StageInput`/`StageOutput`, `StoryBible`, etc. |
| `backend/storyloom/core/pipeline.py` | `PipelineOrchestrator` — runs stages sequentially, handles revision loops (max 2 retries), supports cancellation |
| `backend/storyloom/core/stages/` | Stage implementations: `planner`, `writer`, `editor`, `continuity`, `quality_gate` |
| `backend/storyloom/providers/` | LLM providers (`anthropic`, `openai`, `deepseek`, `ollama`), `router.py` maps `(stage, language)` → model, `pricing.py` |
| `backend/storyloom/memory/` | Async SQLite persistence (`SQLiteStore`), vector store, file-based SQL migrations, domain models (`Character`, `ChapterRecord`, `PlotThread`, `WorldStateEntry`) |
| `backend/storyloom/output/` | Output adapters: filesystem, web publisher |
| `backend/storyloom/config/` | pydantic-settings (`STORYLOOM_*` env vars), YAML pipeline config loader |
| `backend/storyloom/i18n/` | Bilingual prompt templates (`zh/` and `en/`) per stage |
| `backend/storyloom/cli/main.py` | Typer CLI: `init`, `serve`, `run` |
| `backend/storyloom/core/task_queue.py` | In-process async task queue for pipeline tracking |
| `frontend/` | Vue 3 + TypeScript + Vite SPA |
| `frontend/src/pages/` | Route pages: `ProjectList`, `ProjectDetail`, `PipelineRun`, `MemoryExplorer` |
| `frontend/src/api/client.ts` | Typed API client (fetch-based, endpoints for projects, pipeline, memory, chapters) |
| `frontend/src/router/index.ts` | Vue Router with 4 routes (home, project-detail, pipeline-run, memory-explorer) |
| `tests/` | (Root-level, can be migrated) Legacy test directory |

### Vite Dev Proxy

The frontend dev server (`:5173`) proxies `/api` → `http://localhost:8000` and `/ws` → `ws://localhost:8000`, so both services appear on the frontend port during development.

### Key Design Decisions

- **Provider routing**: `(stage, language)` → model (ZH writer uses deepseek-chat, everything else Claude Sonnet by default)
- **Stage contract**: Each stage returns `StageOutput` with `decision: "approved" | "rejected" | "need_revision"`. Revision loops back to writer or editor (max 2 retries before forced pass)
- **Pipeline flow**: Planner → Writer → Editor → Continuity → Quality Gate → Output
- **LLM abstraction**: `LLMProvider` is a `Protocol` (structural typing), not an ABC — any class with an async `complete()` method works
- **Memory**: Async SQLite via `aiosqlite`, SQL migrations run from `memory/migrations/` in sorted order
- **Tests**: pytest with `asyncio_mode = "auto"` at `backend/tests/`

## Always-On Skills

When doing any code writing, reviewing, or refactoring, you MUST invoke the `karpathy-guidelines` skill before proceeding. It is already installed and enabled.

## Development Rules

1. **Code review + test-first**: Every code change must be reviewed and accompanied by corresponding tests (unit tests + integration tests). Prefer TDD: write tests before implementation, ensure they fail first, then make them pass. Use the `test-driven-development` skill when available.

2. **Prefer existing open-source solutions**: Before implementing any feature, search for existing open-source libraries that already solve the problem. Avoid reinventing well-established functionality. For example, instead of building custom LLM provider wrappers, use [LiteLLM](https://github.com/BerriAI/litellm) — it provides a unified interface to 100+ providers (OpenAI, Anthropic, Gemini, Bedrock, etc.) with the OpenAI-compatible format. Similarly, use battle-tested libraries for vector stores, caching, task queues, etc. rather than building from scratch. Only build custom when the existing solutions don't fit the specific requirements.

3. **LLM-driven control flow**: Design code so that LLMs make autonomous decisions rather than being constrained by rigid code logic. Favor patterns where the LLM chooses the path (e.g., stage `decision` field with `approved`/`rejected`/`need_revision`, provider routing by context). Avoid hardcoded if/else chains that could be replaced by LLM judgment. Each pipeline stage should be an LLM agent that decides what to do next, not a deterministic function.

### Environment Variables

Backend settings are loaded from `STORYLOOM_*` env vars via pydantic-settings (`backend/storyloom/config/settings.py`):
- `STORYLOOM_DATABASE_URL` — defaults to `sqlite:///./storyloom.db`
- `STORYLOOM_LOG_LEVEL` — defaults to `INFO`
- `STORYLOOM_LLM_PROVIDERS` — JSON dict of provider configs
