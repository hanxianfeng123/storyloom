# Storyloom

> [🇨🇳 中文](README.zh.md)

<div align="right">
  <a href="README.md">🏠 Home</a>
</div>

# Storyloom — English

Storyloom is an AI-powered novel generation platform that orchestrates multiple LLMs into a coherent creative pipeline, from plot planning to finished chapters.

## Key Features

- **Multi-LLM Pipeline** — Each stage (planner, writer, editor, continuity, quality gate) can use a different model provider, optimized for its specific task
- **Persistent Memory** — Characters, plot threads, and world state are automatically maintained across chapters for long-form consistency
- **Bilingual** — Full support for English and Chinese, with language-aware model routing
- **Extensible** — Plugin architecture for custom stages, models, and output formats
- **Real-time Progress** — WebSocket-powered pipeline progress streaming with frontend visualization

## Pipeline Architecture

```text
User Prompt → Planner → Writer → Editor → Continuity → Quality Gate → Output
```

Each stage is an autonomous AI agent with `approved` / `need_revision` decision capability, supporting up to 2 revision loops.

### Stage Overview

| Stage | Responsibility |
|-------|---------------|
| **Planner** | Generates plot outlines, character arcs, and chapter structures from user prompts |
| **Writer** | Produces prose for each chapter following the plan, configurable for different styles and genres |
| **Editor** | Revises output for grammar, pacing, and consistency with the overall narrative |
| **Continuity** | Tracks characters, locations, timelines, and plot threads across chapters |
| **Quality Gate** | Evaluates output against quality metrics (readability, coherence, style adherence) |
| **Output** | Formats the final novel into Markdown, EPUB, PDF, etc. |

## Quick Start

```bash
# Install
pip install storyloom

# Initialize a project
storyloom init my-novel

# Start the API server
storyloom serve

# Start frontend dev server (separate terminal)
make frontend-dev
```

### Tech Stack

- **Backend**: Python / FastAPI / LiteLLM / SQLite + aiosqlite
- **Frontend**: Vue 3 + TypeScript + Vite
- **Deployment**: Docker Compose

## Configuration

Copy `.env.example` to `.env` and fill in your API keys:

```bash
# LiteLLM reads these env vars automatically
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
```

Default model routing:
- **Chinese writing**: DeepSeek Chat
- **Other stages**: Claude Sonnet

## License

MIT
