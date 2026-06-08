<div align="right">
  <a href="README.en.md">🇬🇧 English</a>
</div>

# Storyloom

多模型 AI 小说创作平台 — 编排多个大语言模型，从构思到成书。

## 核心特性

- **多模型流水线** — 不同阶段（规划、写作、编辑、连续性检查、质量把关）可配置不同的 LLM
- **持久化记忆** — 角色档案、剧情线索、世界观跨章节自动维护
- **双语支持** — 中英文创作，语言感知的路由编排
- **可扩展** — 插件式架构，支持自定义阶段、模型和输出格式
- **实时监控** — WebSocket 推送流水线进度，前端可视化跟踪

## 流水线架构

```text
用户需求 → 规划 → 写作 → 编辑 → 连续性检查 → 质量把关 → 输出
```

每个阶段是自主 AI Agent，输出 `approved` / `need_revision` 决策，支持最多 2 轮修订。

### 阶段说明

| 阶段 | 职责 |
|------|------|
| **规划** | 生成故事大纲、角色弧光和章节结构 |
| **写作** | 按规划撰写章节正文，支持不同风格和体裁 |
| **编辑** | 修正语法、节奏和叙事一致性 |
| **连续性检查** | 追踪角色、地点、时间线和剧情线索 |
| **质量把关** | 评估可读性、连贯性、风格一致性 |
| **输出** | 格式化输出 Markdown、EPUB、PDF |

## 快速开始

```bash
pip install storyloom
storyloom init my-novel
storyloom serve
```

### 技术栈

- **后端**: Python / FastAPI / LiteLLM / SQLite
- **前端**: Vue 3 + TypeScript + Vite
- **部署**: Docker Compose

## 配置

```bash
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
```

## License

MIT
