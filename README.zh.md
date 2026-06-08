# Storyloom

> [🇬🇧 English](README.en.md)

<div align="right">
  <a href="README.md">🏠 返回首页</a>
</div>

# Storyloom — 中文介绍

Storyloom 是一个基于 AI 的小说创作平台，通过编排多个大语言模型，实现从构思到成书的完整创作流程。

## 核心特性

- **多模型流水线** — 不同创作阶段（规划、写作、编辑、连续性检查、质量把关）可配置不同的 LLM 模型，各取所长
- **持久化记忆** — 角色档案、剧情线索、世界观设定跨章节自动维护，长篇小说保持连贯
- **双语支持** — 支持中文和英文的创作与生成，语言感知的路由编排
- **可扩展** — 插件式架构，支持自定义阶段、模型和输出格式
- **实时监控** — WebSocket 推送流水线进度，前端可视化跟踪

## 流水线架构

```text
用户需求 → 规划 → 写作 → 编辑 → 连续性检查 → 质量把关 → 输出
```

每个阶段都是一个自主的 AI Agent，输出 `approved` / `need_revision` 决策，支持最多 2 轮修订循环。

### 阶段说明

| 阶段 | 职责 |
|------|------|
| **规划** | 根据用户提示生成故事大纲、角色弧光和章节结构 |
| **写作** | 按照规划撰写章节正文，支持不同风格和体裁 |
| **编辑** | 修正语法、节奏和叙事一致性 |
| **连续性检查** | 追踪角色、地点、时间线和剧情线索，确保跨章节连贯 |
| **质量把关** | 从可读性、连贯性、风格一致性等维度评估输出质量 |
| **输出** | 将最终作品格式化为 Markdown、EPUB、PDF 等格式 |

## 快速开始

```bash
# 安装
pip install storyloom

# 初始化项目
storyloom init my-novel

# 启动 API 服务
storyloom serve

# 启动前端开发服务器（单独终端）
make frontend-dev
```

### 技术栈

- **后端**: Python / FastAPI / LiteLLM / SQLite + aiosqlite
- **前端**: Vue 3 + TypeScript + Vite
- **部署**: Docker Compose

## 配置

创建 `.env` 文件（参考 `.env.example`）填入 API Key：

```bash
# LiteLLM 会自动读取以下环境变量
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
```

默认模型路由：
- **中文写作**: DeepSeek Chat
- **其他阶段**: Claude Sonnet

## License

MIT
