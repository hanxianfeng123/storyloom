<div align="right">
  <a href="README.md">🏠 首页</a> · <a href="README.en.md">🇬🇧 English</a>
</div>

<br>

<p align="center">
  <img src="https://raw.githubusercontent.com/hanxianfeng123/storyloom/main/assets/logo.png" alt="Storyloom" width="120" onerror="this.style.display='none'" />
</p>

<h1 align="center">Storyloom</h1>

<p align="center">
  <em>多模型 AI 小说创作平台 —— 从构思到成书，一气呵成</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/storyloom">
    <img src="https://img.shields.io/pypi/v/storyloom?color=%2334D058&label=版本" alt="PyPI">
  </a>
  <a href="https://github.com/hanxianfeng123/storyloom/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/hanxianfeng123/storyloom/ci.yml?branch=main&label=构建" alt="CI">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/github/license/hanxianfeng123/storyloom?color=blue&label=许可" alt="License">
  </a>
  <a href="https://www.python.org">
    <img src="https://img.shields.io/badge/python-3.11+-blue?label=Python" alt="Python">
  </a>
</p>

---

Storyloom 是一个 AI 驱动的小说创作平台。它通过编排多个大语言模型，构建了一条从故事规划、章节写作、编辑修正到质量把关的完整创作流水线，配合持久化记忆系统，让长篇小说创作保持连贯一致。

## 核心特性

- **🧩 多模型流水线** — 规划、写作、编辑、连续性检查、质量把关各阶段可独立配置 LLM 模型，各取所长
- **🧠 持久化记忆** — 角色档案、剧情线索、世界观设定跨章节自动维护，告别前后矛盾
- **🌏 双语支持** — 支持中文和英文创作，语言感知的模型路由编排
- **🔌 可扩展** — 插件式架构，支持自定义阶段、模型和输出格式
- **📊 实时进度** — WebSocket 推送流水线执行进度，前端可视化实时跟踪

## 流水线架构

```text
用户需求 → 规划 → 写作 → 编辑 → 连续性检查 → 质量把关 → 输出
```

每个阶段是一个自主的 AI Agent，输出 `approved` / `need_revision` / `rejected` 决策，支持最多 **2 轮修订循环**，确保输出质量。

| 阶段 | 职责 |
|------|------|
| **规划** | 根据用户提示生成故事大纲、角色弧光和章节结构 |
| **写作** | 按规划撰写章节正文，支持不同风格和体裁 |
| **编辑** | 修正语法、节奏和叙事一致性 |
| **连续性检查** | 追踪角色、地点、时间线和剧情线索，确保跨章节连贯 |
| **质量把关** | 从可读性、连贯性、风格一致性等多维度评估输出质量 |
| **输出** | 将最终作品格式化为 Markdown、EPUB、PDF 等格式 |

## 快速开始

### 安装

```bash
pip install storyloom
```

### 初始化项目

```bash
storyloom init my-novel
cd my-novel
```

### 启动服务

```bash
# 启动 API 服务
storyloom serve

# 或使用 Docker
docker compose up -d
```

### 前端开发

```bash
# 单独终端运行
make backend-dev   # API 服务 :8000
make frontend-dev  # 前端界面 :5173
```

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.11+ / FastAPI / LiteLLM / aiosqlite |
| **前端** | Vue 3 + TypeScript + Vite |
| **LLM 提供商** | Anthropic Claude · DeepSeek · OpenAI · Ollama |
| **部署** | Docker Compose |

## 配置

复制 `.env.example` 为 `.env`，填入 API Key：

```bash
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
```

> LiteLLM 会自动读取以上环境变量，无需额外配置。

### 默认模型路由

| 阶段 | 中文 | English |
|------|------|---------|
| 规划 | Claude Sonnet | Claude Sonnet |
| 写作 | DeepSeek Chat | Claude Sonnet |
| 编辑 | Claude Sonnet | Claude Sonnet |
| 连续性检查 | Claude Haiku | Claude Haiku |
| 质量把关 | Claude Sonnet | Claude Sonnet |

## 项目结构

```
storyloom/
├── backend/
│   └── storyloom/
│       ├── core/          # 流水线编排 + 各阶段实现
│       ├── providers/     # LLM 提供商封装
│       ├── memory/        # 持久化记忆系统
│       ├── config/        # 配置加载
│       ├── i18n/          # 中英文提示词模板
│       └── api/           # FastAPI 路由
├── frontend/              # Vue 3 SPA
└── docker-compose.yml
```

## License

[MIT](LICENSE) © 2024 hanxianfeng123
