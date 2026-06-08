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

Storyloom is an AI-powered novel generation platform. Multiple autonomous AI agents collaborate in a swarm — from plot planning and chapter writing to editing, continuity checking, and quality assurance — with every step decided by LLM judgment, not hardcoded logic. Its persistent memory system ensures consistency across long-form narratives.

## Key Features

- **🧩 Multi-Agent Swarm** — Each writing role is an autonomous AI agent, collaborating freely through a message bus. LLMs make decisions, not hardcoded logic
- **🧠 Shared Blackboard** — Agents share results via a blackboard; characters, plot threads, and world state are automatically maintained across chapters
- **🌏 Bilingual** — Full support for English and Chinese, with language-aware model configuration
- **🔌 Extensible** — Plugin architecture for custom agents, LLM providers, and output formats
- **📊 Real-time Progress** — WebSocket-powered progress streaming with frontend visualization

## Architecture

### Philosophy: The Framework Doesn't Orchestrate — Agents Decide

Traditional pipelines use code to control execution order and error handling. Storyloom's Agent Swarm is different — the framework provides only three primitives; how agents collaborate is entirely up to the LLM:

```
┌─────────────────────────────────────────────────────┐
│  novel layer (business logic)                        │
│  - defines agent tree (who's in which group)         │
│  - defines prompts (role cards)                      │
│  - seeds initial data, waits for chief decision      │
├─────────────────────────────────────────────────────┤
│  swarm framework (infrastructure)                    │
│  ┌───────────────────────────────────────────────┐  │
│  │ Message Bus — free-form agent conversation     │  │
│  │  · direct: agent → agent                      │  │
│  │  · group: agent → entire group                │  │
│  │  · broadcast: agent → everyone                │  │
│  ├───────────────────────────────────────────────┤  │
│  │ Blackboard — shared workspace                  │  │
│  │  · structured KV store with versioned history  │  │
│  │  · watch(key_pattern) → change notification   │  │
│  ├───────────────────────────────────────────────┤  │
│  │ Agent Runtime — each agent runs its own loop   │  │
│  │  · perceive → think → act                     │  │
│  │  · doesn't decide "what to do" — that's LLM's job  │
│  └───────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  providers (pluggable LLM)                           │
│  ├── LitellmProvider                                 │
│  ├── CAMELAgent (planned)                            │
│  └── MockProvider (testing)                          │
└─────────────────────────────────────────────────────┘
```

### How It Works

```
1. Initial context is written to the blackboard (story bible, character cards, world state)
2. All agents start → each enters its perceive loop
3. Planner detects a change → LLM decides to plan the arc outline
4. Writer detects the plan → LLM decides to write chapters
5. Continuity finds a contradiction → sends a direct message to the relevant writer
6. Editor polishes → Quality reviews → Chief editor makes the final call
7. Loop continues until the chief approves
```

Agents can **talk directly** (via message bus) or **collaborate indirectly** (via blackboard). The framework never decides "what should happen next" — that's always the LLM's judgment call.

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

## License

[MIT](LICENSE) © 2024 hanxianfeng123
