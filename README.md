<div align="right">
  <a href="README.en.md">🇬🇧 English</a>
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

<p align="center">
  <a href="#核心特性">核心特性</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="#架构设计">架构设计</a> ·
  <a href="#技术栈">技术栈</a> ·
  <a href="#配置">配置</a> ·
  <a href="README.en.md">English</a>
</p>

---

Storyloom 是一个 AI 驱动的小说创作平台。它通过多个自主 AI Agent 协同工作（Agent Swarm），从故事规划、章节写作、编辑修正到质量把关，全流程由 LLM 自主决策。配合持久化记忆系统，让长篇小说创作保持连贯一致。

## 核心特性

- **🧩 多 Agent 蜂群** — 每个写作角色是一个自主 AI Agent，通过消息总线自由协作，LLM 自主决策而非代码编排
- **🧠 共享黑板** — Agent 之间通过黑板共享结果，角色档案、剧情线索、世界观设定跨章节自动维护
- **🌏 双语支持** — 支持中文和英文创作，语言感知的模型路由配置
- **🔌 可扩展** — 插件式架构，支持自定义 Agent、LLM Provider 和输出格式
- **📊 实时进度** — WebSocket 推送执行进度，前端可视化实时跟踪

## 架构设计

### 核心理念：框架不做编排，Agent 自主决定

传统流水线由代码控制执行顺序和错误处理。Storyloom 的 Agent Swarm 架构不同——框架只提供三样东西，Agent 之间如何协作完全由 LLM 自主决定：

```
┌─────────────────────────────────────────────────────┐
│  novel layer (业务层)                                │
│  - 定义 agent 树（谁在群里）                          │
│  - 定义 prompt（角色卡）                              │
│  - 写入初始数据，等总编决策                            │
├─────────────────────────────────────────────────────┤
│  swarm framework (基础设施)                           │
│  ┌───────────────────────────────────────────────┐  │
│  │ Message Bus — agent 之间自由对话               │  │
│  │  · direct: agent → agent                      │  │
│  │  · group: agent → 整个组                      │  │
│  │  · broadcast: agent → 所有人                  │  │
│  ├───────────────────────────────────────────────┤  │
│  │ Blackboard — 共享工作区                        │  │
│  │  · 结构化 KV 存储，版本化历史                    │  │
│  │  · watch(key_pattern) → 变化通知              │  │
│  ├───────────────────────────────────────────────┤  │
│  │ Agent Runtime — 每个 agent 独立循环             │  │
│  │  · 感知 → 思考 → 行动                          │  │
│  │  · 不决定"该做什么"，那是 LLM 的事              │  │
│  └───────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  providers (可插拔 LLM)                              │
│  ├── LitellmProvider                                 │
│  ├── CAMELAgent (计划中)                             │
│  └── MockProvider (测试)                             │
└─────────────────────────────────────────────────────┘
```

### 工作机制

```
1. 初始数据写入黑板（故事设定、角色卡、世界观）
2. 启动所有 Agent → 每个 Agent 进入感知循环
3. Planner 感知到黑板变化 → LLM 决定规划篇章弧
4. Writer 感知到规划完成 → LLM 决定开始写作
5. Continuity 发现矛盾 → 发消息给对应 Writer
6. Editor 润色 → Quality 评审 → Chief 总编决策
7. 循环往复，直到总编批准
```

Agent 之间可以**直接对话**，也可以**通过黑板间接协作**，一切由 LLM 自主判断。框架从不决定"下一步该做什么"。

### 项目结构

```
storyloom/
├── backend/
│   └── storyloom/
│       ├── core/              # (迁移中) 原流水线实现
│       ├── swarm/             # Agent Swarm 框架
│       │   ├── models.py      # AgentNode, Message, BlackboardEntry
│       │   ├── blackboard.py  # 共享黑板（KV + 模式监听）
│       │   ├── message_bus.py # 消息总线（直接/组播/广播）
│       │   ├── provider.py    # AgentProvider 协议
│       │   ├── runtime.py     # Agent 循环（感知→思考→行动）
│       │   ├── providers/     # LLM Provider 实现
│       │   └── novel/         # 小说写作业务层
│       │       ├── prompts.py     # 中文 Agent Prompt
│       │       ├── tree_factory.py # 构建 Agent 树
│       │       └── orch.py        # run_story_arc() 入口
│       ├── providers/         # LLM 提供商封装
│       ├── memory/            # 持久化系统
│       ├── config/            # 配置加载
│       ├── i18n/              # 中英文提示词模板
│       └── api/               # FastAPI 路由
├── frontend/                  # Vue 3 SPA
└── docker-compose.yml
```

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

## License

[MIT](LICENSE) © 2024 hanxianfeng123
