<div align="right">
  <a href="README.md">🇨🇳 中文</a>
</div>

<br>

<p align="center">
  <img src="https://raw.githubusercontent.com/hanxianfeng123/storyloom/main/assets/logo.png" alt="Storyloom" width="120" onerror="this.style.display='none'" />
</p>

<h1 align="center">Storyloom</h1>

<p align="center">
  <em>Multi-LLM Novel Generation Platform — From Idea to Publication</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/storyloom">
    <img src="https://img.shields.io/pypi/v/storyloom?color=%2334D058&label=version" alt="PyPI">
  </a>
  <a href="https://github.com/hanxianfeng123/storyloom/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/hanxianfeng123/storyloom/ci.yml?branch=main&label=build" alt="CI">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/github/license/hanxianfeng123/storyloom?color=blue&label=license" alt="License">
  </a>
  <a href="https://www.python.org">
    <img src="https://img.shields.io/badge/python-3.11+-blue?label=Python" alt="Python">
  </a>
</p>

<p align="center">
  <a href="#key-features">Key Features</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#pipeline-architecture">Pipeline</a> ·
  <a href="#tech-stack">Tech Stack</a> ·
  <a href="#configuration">Configuration</a> ·
  <a href="README.md">中文</a>
</p>

---

Storyloom is an AI-powered novel generation platform that orchestrates multiple large language models into a coherent creative pipeline — from plot planning and chapter writing to editing and quality assurance. Its persistent memory system ensures consistency across long-form narratives.

## Key Features

- **🧩 Multi-LLM Pipeline** — Each stage (planner, writer, editor, continuity, quality gate) can use a different model provider, optimized for its specific task
- **🧠 Persistent Memory** — Characters, plot threads, and world state are automatically maintained across chapters — no more contradictions
- **🌏 Bilingual** — Full support for English and Chinese, with language-aware model routing
- **🔌 Extensible** — Plugin architecture for custom stages, models, and output formats
- **📊 Real-time Progress** — WebSocket-powered pipeline progress streaming with frontend visualization

## Pipeline Architecture

```text
User Prompt → Planner → Writer → Editor → Continuity → Quality Gate → Output
```

Each stage is an autonomous AI agent with `approved` / `need_revision` / `rejected` decision capability, supporting up to **2 revision loops** for quality assurance.

| Stage | Responsibility |
|-------|---------------|
| **Planner** | Generates plot outlines, character arcs, and chapter structures from user prompts |
| **Writer** | Produces prose for each chapter following the plan, configurable for different styles and genres |
| **Editor** | Revises output for grammar, pacing, and narrative consistency |
| **Continuity** | Tracks characters, locations, timelines, and plot threads across chapters |
| **Quality Gate** | Evaluates readability, coherence, and style adherence |
| **Output** | Formats the final novel into Markdown, EPUB, PDF, etc. |

## Quick Start

### Install

```bash
pip install storyloom
```

### Initialize a Project

```bash
storyloom init my-novel
cd my-novel
```

### Start the Server

```bash
# Start the API server
storyloom serve

# Or use Docker
docker compose up -d
```

### Frontend Development

```bash
# Run in separate terminals
make backend-dev   # API server :8000
make frontend-dev  # Frontend :5173
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+ / FastAPI / LiteLLM / aiosqlite |
| **Frontend** | Vue 3 + TypeScript + Vite |
| **LLM Providers** | Anthropic Claude · DeepSeek · OpenAI · Ollama |
| **Deployment** | Docker Compose |

## Configuration

Copy `.env.example` to `.env` and fill in your API keys:

```bash
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
```

> LiteLLM reads these environment variables automatically — no additional setup required.

### Default Model Routing

| Stage | 中文 | English |
|-------|------|---------|
| Planner | Claude Sonnet | Claude Sonnet |
| Writer | DeepSeek Chat | Claude Sonnet |
| Editor | Claude Sonnet | Claude Sonnet |
| Continuity | Claude Haiku | Claude Haiku |
| Quality Gate | Claude Sonnet | Claude Sonnet |

## Project Structure

```
storyloom/
├── backend/
│   └── storyloom/
│       ├── core/          # Pipeline orchestration + stage implementations
│       ├── providers/     # LLM provider wrappers
│       ├── memory/        # Persistent memory system
│       ├── config/        # Configuration loading
│       ├── i18n/          # Bilingual prompt templates
│       └── api/           # FastAPI routes
├── frontend/              # Vue 3 SPA
└── docker-compose.yml
```

## Contributing

Contributions welcome! See the [Contributing Guide](CONTRIBUTING.md).

## License

[MIT](LICENSE) © 2024 hanxianfeng123
