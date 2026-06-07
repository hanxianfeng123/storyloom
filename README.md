# Storyloom

> 多模型 AI 小说创作平台 — 多 LLM 编排、持久化记忆、双语支持
> Multi-LLM novel generation platform with persistent memory and bilingual support.

---

## 中文介绍

Storyloom 是一个基于 AI 的小说创作平台，通过编排多个大语言模型，实现从构思到成书的完整创作流程。

### 核心特性

- **多模型流水线** — 不同创作阶段（规划、写作、编辑、连续性检查、质量把关）可配置不同的 LLM 模型，各取所长
- **持久化记忆** — 角色档案、剧情线索、世界观设定跨章节自动维护，长篇小说保持连贯
- **双语支持** — 支持中文和英文的创作与生成，语言感知的路由编排
- **可扩展** — 插件式架构，支持自定义阶段、模型和输出格式
- **实时监控** — WebSocket 推送流水线进度，前端可视化跟踪

### 流水线架构

```text
用户需求 → 规划 → 写作 → 编辑 → 连续性检查 → 质量把关 → 输出
```

每个阶段都是一个自主的 AI Agent，输出 `approved` / `need_revision` 决策，支持最多 2 轮修订循环。

### 快速开始

```bash
# 安装
pip install storyloom

# 初始化项目
storyloom init my-novel

# 启动 API 服务
storyloom serve
```

---

## English

Storyloom is an AI-powered novel generation platform that orchestrates multiple LLMs into a coherent creative pipeline, from plot planning to finished chapters.

### Key Features

- **Multi-LLM Pipeline** — Each stage (planner, writer, editor, continuity, quality gate) can use a different model provider, optimized for its specific task
- **Persistent Memory** — Characters, plot threads, and world state are automatically maintained across chapters for long-form consistency
- **Bilingual** — Full support for English and Chinese, with language-aware model routing
- **Extensible** — Plugin architecture for custom stages, models, and output formats
- **Real-time Progress** — WebSocket-powered pipeline progress streaming with frontend visualization

### Pipeline Architecture

```text
User Prompt → Planner → Writer → Editor → Continuity → Quality Gate → Output
```

Each stage is an autonomous AI agent with `approved` / `need_revision` decision capability, supporting up to 2 revision loops.

### Quick Start

```bash
# Install
pip install storyloom

# Initialize a project
storyloom init my-novel

# Start the API server
storyloom serve
```

---

## License

MIT
