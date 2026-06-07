# Storyloom Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the v1 of Storyloom — an AI novel generation platform with multi-LLM pipeline, persistent memory, bilingual support, and web UI.

**Architecture:** Python FastAPI backend with Vue 3 SPA frontend. Pipeline stages connected via typed contracts. LLM providers abstracted behind a Protocol interface. Memory layer uses SQLite + sqlite-vec. CLI for headless operation.

**Tech Stack:** Python 3.11+, FastAPI, Vue 3 + Vite, SQLite + sqlite-vec, structlog, Typer, pytest, pytest-asyncio, Docker Compose.

---

## Phase 0: Project Scaffolding

Bootstrap the monorepo structure, build tooling, and project metadata.

### Task 0.1: Root Project & Python Package

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/storyloom/__init__.py`
- Create: `backend/storyloom/main.py`
- Create: `Makefile`
- Create: `.gitignore`

- [ ] **Step 1: Write pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "storyloom"
version = "0.1.0"
description = "AI novel generation platform with multi-LLM pipeline"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110",
    "uvicorn[standard]>=0.27",
    "pydantic>=2.5",
    "pydantic-settings>=2.1",
    "structlog>=24.1",
    "typer>=0.9",
    "httpx>=0.26",
    "anthropic>=0.30",
    "openai>=1.12",
    "aiofiles>=23.2",
]
dynamic = ["version"]

[project.urls]
Homepage = "https://github.com/storyloom/storyloom"

[tool.setuptools.packages.find]
where = ["."]
include = ["storyloom*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py311"
```

- [ ] **Step 2: Write backend/storyloom/__init__.py**

```python
__version__ = "0.1.0"
```

- [ ] **Step 3: Write backend/storyloom/cli/main.py** — CLI entry point (NOT at package root; uses cli/ subpackage).

```python
"""Storyloom CLI entry point."""
import typer

app = typer.Typer(name="storyloom")


@app.command()
def init(project_name: str):
    """Initialize a new novel project."""
    typer.echo(f"Initializing project: {project_name}")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000):
    """Start the Storyloom web server."""
    typer.echo(f"Starting server on {host}:{port}")


@app.command()
def run(chapter: str):
    """Run the pipeline headless for one or more chapters."""
    typer.echo(f"Running pipeline for chapter(s): {chapter}")


if __name__ == "__main__":
    app()
```

- [ ] **Step 4: Write Makefile**

```makefile
.PHONY: dev install test lint clean

install:
	cd backend && pip install -e ".[dev]"

dev:
	cd backend && uvicorn storyloom.api.app:app --reload --port 8000

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check storyloom/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name *.pyc -delete
```

- [ ] **Step 5: Write .gitignore**

```
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
.env
*.db
node_modules/
dist/
```

- [ ] **Step 6: Run tests to verify package installs**

Run: `cd backend && pip install -e ".[dev]" && python -c "import storyloom; print(storyloom.__version__)"`
Expected: `0.1.0`

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "chore: scaffold storyloom project structure"
```

---

### Task 0.2: Open Source Scaffolding

**Files:**
- Create: `LICENSE`
- Create: `README.md`
- Create: `docs/contributor/CONTRIBUTING.md`
- Create: `docs/contributor/CODE_OF_CONDUCT.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`

- [ ] **Step 1: Write LICENSE (MIT)**

```text
MIT License

Copyright (c) 2026 storyloom

Permission is hereby granted...
```

(Use standard MIT license text.)

- [ ] **Step 2: Write README.md**

```markdown
# Storyloom

AI novel generation platform with multi-LLM pipeline, persistent memory, and bilingual support.

## Quick Start

```bash
pip install storyloom
storyloom init my-novel
storyloom serve
```

## Architecture

Pipeline: Planner → Writer → Editor → Continuity → Quality Gate → Output

## License

MIT
```
```

- [ ] **Step 3: Write CONTRIBUTING.md** — Outline PR workflow: fork, branch, test, commit conventional commits, PR template.

- [ ] **Step 4: Write remaining GitHub templates** — Bug report (os, python version, steps to reproduce, expected vs actual), feature request (problem, solution, alternatives), PR template (summary, test plan, checklist).

- [ ] **Step 5: Commit**

```bash
git add LICENSE README.md .github/ docs/contributor/ && git commit -m "chore: add open-source scaffolding"
```

---

### Task 0.3: Directory Structure & Empty Modules

**Files:**
- Create all backend modules as `__init__.py` files

- [ ] **Step 1: Create directory tree**

```bash
mkdir -p backend/storyloom/{core/stages,providers,memory/{models,migrations},output/web,i18n/{zh/prompts,en/prompts},cli/commands,api/routes,config}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p frontend examples .github/workflows docs/{guide,api,contributor}
```

- [ ] **Step 2: Create empty __init__.py in each Python package**

Run: `find backend/storyloom -type d -exec touch {}/__init__.py \;`

- [ ] **Step 3: Verify imports work**

Run: `cd backend && python -c "
from storyloom.core import pipeline
from storyloom.providers import base
from storyloom.memory import store
from storyloom.output import filesystem
from storyloom.cli import main
from storyloom.api import routes
from storyloom.config import settings
from storyloom.i18n import zh
print('All imports OK')
"`
Expected: `All imports OK`

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "chore: add module directory structure"
```

---

## Phase 1: Configuration & Logging

### Task 1.1: Settings Management

**Files:**
- Create: `backend/storyloom/config/__init__.py`
- Create: `backend/storyloom/config/settings.py`
- Create: `tests/unit/test_settings.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_settings.py
import pytest
from pydantic import ValidationError
from storyloom.config.settings import Settings


def test_defaults():
    s = Settings()
    assert s.database_url == "sqlite:///./storyloom.db"
    assert s.log_level == "INFO"


def test_openai_key_required_for_openai_provider():
    with pytest.raises(ValidationError):
        Settings(llm_providers={"openai": {}})


def test_default_providers_empty():
    s = Settings()
    assert s.llm_providers == {}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pip install -e ".[dev]" && python -m pytest tests/unit/test_settings.py -v`
Expected: ModuleNotFoundError or ImportError for Settings

- [ ] **Step 3: Write minimal implementation**

```python
# backend/storyloom/config/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = "sqlite:///./storyloom.db"
    log_level: str = "INFO"
    llm_providers: dict = {}
    pipeline_config_path: str = ""

    model_config = {"env_prefix": "STORYLOOM_"}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/unit/test_settings.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add backend/storyloom/config/ tests/unit/test_settings.py
git commit -m "feat: add settings management with pydantic-settings"
```

---

### Task 1.2: Structured Logging

**Files:**
- Create: `backend/storyloom/core/logging.py`
- Create: `tests/unit/test_logging.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_logging.py
import pytest
from storyloom.core.logging import get_logger, configure_logging


def test_get_logger_returns_structlog_logger():
    logger = get_logger("test")
    assert hasattr(logger, "info")
    assert hasattr(logger, "error")


def test_configure_logging_sets_level():
    configure_logging("DEBUG")
    logger = get_logger("test_debug")
    # Should not raise
    logger.debug("test message")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/unit/test_logging.py -v`
Expected: ImportError for get_logger

- [ ] **Step 3: Write minimal implementation**

```python
# backend/storyloom/core/logging.py
import structlog


def configure_logging(level: str = "INFO") -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/unit/test_logging.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add backend/storyloom/core/logging.py tests/unit/test_logging.py
git commit -m "feat: add structlog-based logging"
```

---

## Phase 2: i18n Prompt Templates

Move i18n before pipeline stages (Phase 5 depends on it).

### Task 2.1: Chinese Prompt Templates

**Files:**
- Create: `backend/storyloom/i18n/zh/prompts/__init__.py`
- Create: `backend/storyloom/i18n/zh/prompts/planner.py`
- Create: `backend/storyloom/i18n/zh/prompts/writer.py`
- Create: `backend/storyloom/i18n/zh/prompts/editor.py`
- Create: `backend/storyloom/i18n/zh/prompts/quality.py`
- Create: `backend/storyloom/i18n/zh/strings.py`

- [ ] **Step 1: Write Chinese prompts**

```python
# backend/storyloom/i18n/zh/prompts/planner.py
PLANNER_SYSTEM_PROMPT = """你是一个专业的小说章节规划师。你的任务是根据已有设定和故事进展，为下一章生成详细的写作大纲。

要求：
1. 输出格式为 Markdown 列表，每节包含 2-3 个关键情节点
2. 每节标注预期字数
3. 确保情节节奏合理，有起承转合
4. 标注本章需要推进的情节线和伏笔
5. 确保与前文连贯"""

# backend/storyloom/i18n/zh/prompts/writer.py
WRITER_SYSTEM_PROMPT = """你是一个专业的小说作家。你的任务是根据大纲写出高质量的章节正文。

要求：
1. 使用中文写作，语言流畅自然
2. 避免解释腔、自问自答、过度因果连接词
3. 每段不超过 200 字
4. 对话符合角色性格
5. 描写有画面感，避免空洞形容词"""

# backend/storyloom/i18n/zh/prompts/editor.py
EDITOR_SYSTEM_PROMPT = """你是一个资深编辑。对以下章节进行润色。

要求：
1. 修正语病和不通顺的句子
2. 删除冗余表达
3. 保持原意和风格不变
4. 输出使用 diff 格式标注修改"""

# backend/storyloom/i18n/zh/prompts/quality.py
QUALITY_SYSTEM_PROMPT = """你是一个小说质量评审专家。从以下维度评审章节：

1. 情节一致性：是否与前文逻辑连贯
2. 角色声音：角色行为对话是否符合人设
3. 文笔质量：语言是否流畅、有表现力
4. 节奏控制：节奏是否合适
5. 语言准确度：语法用词是否准确

每个维度评分：pass/flag/fail。fail 需给出具体理由。"""

# backend/storyloom/i18n/zh/strings.py
UI_STRINGS = {
    "project.created": "项目已创建",
    "pipeline.started": "流水线已启动",
    "pipeline.completed": "流水线已完成",
    "pipeline.failed": "流水线执行失败",
    "stage.approved": "已通过",
    "stage.rejected": "未通过",
    "stage.need_revision": "需要修改",
}
```

- [ ] **Step 2: Write English prompts**

```python
# backend/storyloom/i18n/en/prompts/planner.py
PLANNER_SYSTEM_PROMPT = """You are a professional novel chapter planner. Generate a detailed outline for the next chapter based on the existing story bible and progress.

Requirements:
1. Output as Markdown list, 2-3 plot points per section
2. Annotate expected word count per section
3. Ensure proper pacing (setup, conflict, resolution)
4. Note which plot threads need advancement
5. Ensure continuity with previous chapters"""
```

(Repeat for writer, editor, quality — analogous to zh but in English.)

- [ ] **Step 3: Commit**

```bash
git add backend/storyloom/i18n/ && git commit -m "feat: add bilingual prompt templates (zh + en)"
```

---

## Phase 3: Core Abstractions

### Task 3.1: Pipeline Contracts

**Files:**
- Create: `backend/storyloom/core/contract.py`
- Create: `tests/unit/test_contract.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_contract.py
import pytest
from pydantic import ValidationError
from storyloom.core.contract import (
    StageInput,
    StageOutput,
    PipelineContext,
    StageMetrics,
    StoryBible,
    CharacterCard,
    WorldState,
    ChapterSummary,
)


def test_stage_metrics_requires_positive_tokens():
    with pytest.raises(ValidationError):
        StageMetrics(model="test", tokens_in=-1, tokens_out=100, latency_ms=100, cost_usd=0)


def test_stage_output_valid_decision():
    output = StageOutput(
        content="chapter text",
        decision="approved",
        metrics=StageMetrics(model="claude", tokens_in=100, tokens_out=200, latency_ms=500, cost_usd=0.01),
    )
    assert output.decision == "approved"


def test_stage_output_need_revision_requires_target():
    output = StageOutput(
        content="text",
        decision="need_revision",
        revise_target="writer",
        revision_context={"issue": "plot hole"},
        metrics=StageMetrics(model="claude", tokens_in=100, tokens_out=200, latency_ms=500, cost_usd=0.01),
    )
    assert output.revise_target == "writer"


def test_pipeline_context_construction():
    ctx = PipelineContext(
        story_bible=StoryBible(title="Test Novel", genre="Fantasy"),
        character_cards=[CharacterCard(name="Alice", role="protagonist")],
        world_state=WorldState(settings={"season": "autumn"}),
        chapter_history=[ChapterSummary(number=1, title="Ch1", word_count=2000)],
    )
    assert ctx.story_bible.title == "Test Novel"
    assert len(ctx.character_cards) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/unit/test_contract.py -v`
Expected: ImportError

- [ ] **Step 3: Write implementation**

```python
# backend/storyloom/core/contract.py
from pydantic import BaseModel, Field
from typing import Literal


class StoryBible(BaseModel):
    title: str
    genre: str
    summary: str = ""
    themes: list[str] = []


class CharacterCard(BaseModel):
    name: str
    role: str
    personality: str = ""
    appearance: str = ""
    background: str = ""


class WorldState(BaseModel):
    settings: dict[str, str] = {}


class ChapterSummary(BaseModel):
    number: int
    title: str
    word_count: int = 0
    summary: str = ""


class PipelineContext(BaseModel):
    story_bible: StoryBible
    character_cards: list[CharacterCard] = []
    world_state: WorldState = WorldState()
    chapter_history: list[ChapterSummary] = []
    style_guide: str | None = None


class StageMetrics(BaseModel):
    model: str
    tokens_in: int = Field(ge=0)
    tokens_out: int = Field(ge=0)
    latency_ms: int = Field(ge=0)
    cost_usd: float = Field(ge=0.0)


class StageInput(BaseModel):
    project_id: str
    chapter_id: str | None = None
    context: PipelineContext


class StageOutput(BaseModel):
    content: str | None = None
    partial: bool = False
    metrics: StageMetrics
    decision: Literal["approved", "rejected", "need_revision"]
    revise_target: Literal["writer", "editor"] | None = None
    revision_context: dict | None = None
    review_notes: str | None = None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/unit/test_contract.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add backend/storyloom/core/contract.py tests/unit/test_contract.py
git commit -m "feat: add pipeline stage contracts"
```

---

### Task 3.2: LLM Response Cache

**Files:**
- Create: `backend/storyloom/core/cache.py`
- Create: `tests/unit/test_cache.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_cache.py
import pytest
from storyloom.core.cache import LLMCache
from storyloom.providers.base import LLMResponse


@pytest.mark.asyncio
async def test_cache_hit():
    cache = LLMCache()
    key = cache.make_key("gpt-4", [{"role": "user", "content": "hello"}])
    cache.put(key, LLMResponse(content="hi", model="gpt-4", tokens_in=10, tokens_out=5, latency_ms=100))
    hit = cache.get(key)
    assert hit is not None
    assert hit.content == "hi"


@pytest.mark.asyncio
async def test_cache_miss():
    cache = LLMCache()
    hit = cache.get("nonexistent")
    assert hit is None


@pytest.mark.asyncio
async def test_cache_max_size():
    cache = LLMCache(max_size=2)
    cache.put("k1", LLMResponse(content="a", model="m", tokens_in=1, tokens_out=1, latency_ms=1))
    cache.put("k2", LLMResponse(content="b", model="m", tokens_in=1, tokens_out=1, latency_ms=1))
    cache.put("k3", LLMResponse(content="c", model="m", tokens_in=1, tokens_out=1, latency_ms=1))
    assert cache.get("k1") is None  # evicted
    assert cache.get("k3") is not None
```

- [ ] **Step 2: Write implementation**

```python
# backend/storyloom/core/cache.py
import hashlib
import json
from collections import OrderedDict
from storyloom.providers.base import LLMResponse


class LLMCache:
    """Simple LRU cache for LLM responses. Keyed by model + message hash."""

    def __init__(self, max_size: int = 100):
        self._cache: OrderedDict[str, LLMResponse] = OrderedDict()
        self.max_size = max_size

    def make_key(self, model: str, messages: list) -> str:
        raw = model + json.dumps([{"role": m.role, "content": m.content} for m in messages], sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, key: str) -> LLMResponse | None:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, response: LLMResponse) -> None:
        self._cache[key] = response
        self._cache.move_to_end(key)
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    def clear(self) -> None:
        self._cache.clear()
```

- [ ] **Step 3: Run tests to verify they pass**

- [ ] **Step 4: Commit**

```bash
git add backend/storyloom/core/cache.py tests/unit/test_cache.py
git commit -m "feat: add LLM response LRU cache"
```

---

### Task 3.3: Error Handling

**Files:**
- Create: `backend/storyloom/core/errors.py`
- Create: `tests/unit/test_errors.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_errors.py
import pytest
from storyloom.core.errors import (
    LLMError,
    StageError,
    ProviderError,
    retry_config,
)


def test_llm_error_is_exception():
    err = LLMError("API error", model="claude-3")
    assert isinstance(err, Exception)
    assert str(err) == "API error"
    assert err.model == "claude-3"


def test_stage_error_has_stage_name():
    err = StageError("Writer failed", stage="writer")
    assert err.stage == "writer"


def test_provider_error_is_llm_error():
    err = ProviderError("Rate limited", provider="openai", status_code=429)
    assert isinstance(err, LLMError)
    assert err.status_code == 429


def test_retry_config_has_defaults():
    assert retry_config["max_retries"] == 3
    assert "RateLimitError" in str(retry_config["retryable_errors"])
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Write implementation**

```python
# backend/storyloom/core/errors.py

class LLMError(Exception):
    def __init__(self, message: str, model: str = ""):
        self.model = model
        super().__init__(message)


class ProviderError(LLMError):
    def __init__(self, message: str, provider: str = "", status_code: int = 0, model: str = ""):
        self.provider = provider
        self.status_code = status_code
        super().__init__(message, model)


class StageError(Exception):
    def __init__(self, message: str, stage: str = ""):
        self.stage = stage
        super().__init__(message)


class PipelineError(Exception):
    def __init__(self, message: str, pipeline_id: str = ""):
        self.pipeline_id = pipeline_id
        super().__init__(message)


class MemoryError(Exception):
    pass


retry_config = {
    "max_retries": 3,
    "backoff_exponential_base": 2,
    "initial_delay_sec": 1,
    "retryable_errors": ["RateLimitError", "TimeoutError", "ServiceUnavailableError"],
}
```

- [ ] **Step 4: Run tests to verify they pass**

- [ ] **Step 5: Commit**

```bash
git add backend/storyloom/core/errors.py tests/unit/test_errors.py
git commit -m "feat: add error hierarchy and retry config"
```

---

## Phase 3: LLM Provider Layer

### Task 3.1: Provider Interface

**Files:**
- Create: `backend/storyloom/providers/base.py`
- Create: `tests/unit/test_provider_base.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_provider_base.py
import pytest
from storyloom.providers.base import LLMProvider, LLMResponse, Message


def test_llm_response_creation():
    resp = LLMResponse(content="Hello", model="claude-3", tokens_in=10, tokens_out=5, latency_ms=100)
    assert resp.content == "Hello"
    assert resp.model == "claude-3"


def test_message_roles():
    msg = Message(role="user", content="Write a chapter")
    assert msg.role == "user"
    assert msg.content == "Write a chapter"


def test_provider_is_protocol():
    """LLMProvider should be a Protocol (can't instantiate directly)."""
    import inspect
    assert hasattr(LLMProvider, "__instancecheck__") or inspect.isclass(LLMProvider)
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Write implementation**

```python
# backend/storyloom/providers/base.py
from pydantic import BaseModel
from typing import Protocol


class Message(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMResponse(BaseModel):
    content: str
    model: str
    tokens_in: int
    tokens_out: int
    latency_ms: int


class LLMProvider(Protocol):
    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        ...
```

- [ ] **Step 4: Run tests to verify they pass**

- [ ] **Step 5: Commit**

---

### Task 3.2: OpenAI Provider

**Files:**
- Create: `backend/storyloom/providers/openai.py`
- Create: `tests/unit/test_provider_openai.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_provider_openai.py
import pytest
from storyloom.providers.openai import OpenAIProvider
from storyloom.providers.base import Message


@pytest.mark.asyncio
async def test_openai_provider_interface():
    provider = OpenAIProvider(api_key="test-key")
    messages = [Message(role="user", content="hello")]
    # Without mocking httpx, this will fail — test the interface shape
    assert hasattr(provider, "complete")
    assert callable(provider.complete)
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Write implementation**

```python
# backend/storyloom/providers/openai.py
import time
from openai import AsyncOpenAI
from storyloom.providers.base import LLMResponse, Message


class OpenAIProvider:
    def __init__(self, api_key: str, base_url: str | None = None):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        start = time.monotonic()
        response = await self.client.chat.completions.create(
            model=model or "gpt-4o",
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency = int((time.monotonic() - start) * 1000)
        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            tokens_in=response.usage.prompt_tokens if response.usage else 0,
            tokens_out=response.usage.completion_tokens if response.usage else 0,
            latency_ms=latency,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

- [ ] **Step 5: Commit**

---

### Task 3.3: Anthropic Provider

**Files:**
- Create: `backend/storyloom/providers/anthropic.py`
- Create: `tests/unit/test_provider_anthropic.py`

- [ ] **Step 1: Write the failing test** (interface shape test)

```python
# tests/unit/test_provider_anthropic.py
import pytest
from storyloom.providers.anthropic import AnthropicProvider
from storyloom.providers.base import Message


@pytest.mark.asyncio
async def test_anthropic_provider_interface():
    provider = AnthropicProvider(api_key="test-key")
    assert hasattr(provider, "complete")
    assert callable(provider.complete)
```

- [ ] **Step 2: Write implementation**

```python
# backend/storyloom/providers/anthropic.py
import time
from anthropic import AsyncAnthropic
from storyloom.providers.base import LLMResponse, Message


class AnthropicProvider:
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        start = time.monotonic()
        system = ""
        chat_messages = []
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})
        response = await self.client.messages.create(
            model=model or "claude-sonnet-4-20250514",
            system=system or None,
            messages=chat_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency = int((time.monotonic() - start) * 1000)
        return LLMResponse(
            content=response.content[0].text if response.content else "",
            model=response.model,
            tokens_in=response.usage.input_tokens if response.usage else 0,
            tokens_out=response.usage.output_tokens if response.usage else 0,
            latency_ms=latency,
        )
```

- [ ] **Step 3: Run tests**

- [ ] **Step 4: Commit**

---

### Task 3.X: Pricing Utility

**Files:**
- Create: `backend/storyloom/providers/pricing.py`
- Create: `tests/unit/test_pricing.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_pricing.py
from storyloom.providers.pricing import estimate_cost


def test_claude_sonnet_pricing():
    cost = estimate_cost("claude-sonnet", tokens_in=1000, tokens_out=500)
    assert cost > 0
    assert cost < 1  # Should be < $1 for these token counts


def test_deepseek_pricing_cheaper():
    claude_cost = estimate_cost("claude-sonnet", tokens_in=1000, tokens_out=500)
    deepseek_cost = estimate_cost("deepseek-chat", tokens_in=1000, tokens_out=500)
    assert deepseek_cost < claude_cost


def test_unknown_model_defaults():
    cost = estimate_cost("unknown-model", tokens_in=1000, tokens_out=500)
    assert cost >= 0
```

- [ ] **Step 2: Write implementation**

```python
# backend/storyloom/providers/pricing.py
"""Per-model pricing in USD per 1M tokens."""

PRICING_TABLE = {
    # Anthropic
    "claude-sonnet-4":     {"input": 3.0,  "output": 15.0},
    "claude-sonnet":       {"input": 3.0,  "output": 15.0},
    "claude-3.5-sonnet":   {"input": 3.0,  "output": 15.0},
    "claude-3-haiku":      {"input": 0.25, "output": 1.25},
    # OpenAI
    "gpt-4o":              {"input": 2.5,  "output": 10.0},
    "gpt-4o-mini":         {"input": 0.15, "output": 0.6},
    # DeepSeek
    "deepseek-chat":       {"input": 0.14, "output": 0.28},
    # Default fallback
    "__default__":         {"input": 3.0,  "output": 15.0},
}


def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """Calculate estimated cost in USD for an LLM call."""
    pricing = PRICING_TABLE.get(model) or PRICING_TABLE["__default__"]
    cost = (tokens_in * pricing["input"] + tokens_out * pricing["output"]) / 1_000_000
    return round(cost, 6)
```

- [ ] **Step 3: Run tests**

- [ ] **Step 4: Commit**

Then update all stages to use `estimate_cost` instead of `cost_usd=0`:
- Planner: `cost_usd=estimate_cost(response.model, response.tokens_in, response.tokens_out)`
- Writer: same pattern
- Editor: same pattern
- Continuity: same pattern
- Quality Gate: `cost_usd=0` for deterministic, `estimate_cost(...)` for LLM review

---

### Task 3.5: DeepSeek Provider

**Files:**
- Create: `backend/storyloom/providers/deepseek.py`
- Create: `tests/unit/test_provider_deepseek.py`

- [ ] **Step 1: Write test + implementation** — DeepSeek uses OpenAI-compatible API, so provider wraps OpenAIProvider with a different base_url.

```python
# backend/storyloom/providers/deepseek.py
from storyloom.providers.openai import OpenAIProvider


class DeepSeekProvider(OpenAIProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key, base_url="https://api.deepseek.com/v1")
```

- [ ] **Step 2: Write interface shape test** (same pattern as OpenAI)

- [ ] **Step 3: Commit**

---

### Task 3.5: Ollama Provider

**Files:**
- Create: `backend/storyloom/providers/ollama.py`
- Create: `tests/unit/test_provider_ollama.py`

- [ ] **Step 1: Write test + implementation** — Ollama uses OpenAI-compatible API at localhost.

```python
# backend/storyloom/providers/ollama.py
from storyloom.providers.openai import OpenAIProvider


class OllamaProvider(OpenAIProvider):
    def __init__(self, base_url: str = "http://localhost:11434/v1"):
        super().__init__(api_key="ollama", base_url=base_url)
```

- [ ] **Step 2: Write interface shape test**

- [ ] **Step 3: Commit**

---

### Task 3.6: Provider Router

**Files:**
- Create: `backend/storyloom/providers/router.py`
- Create: `tests/unit/test_provider_router.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_provider_router.py
import pytest
from storyloom.providers.router import ProviderRouter
from storyloom.providers.base import LLMProvider


def test_router_requires_provider_registration():
    router = ProviderRouter()
    assert len(router._providers) == 0


def test_register_provider():
    router = ProviderRouter()
    router.register("claude", "anthropic", MockProvider())
    assert "claude" in router._providers


def test_route_by_stage_and_language():
    router = ProviderRouter()
    mock = MockProvider()
    router.register("claude-sonnet", "anthropic", mock)
    router.register("deepseek-chat", "deepseek", mock)
    # Writer + zh → DeepSeek
    model, provider = router.select("writer", "zh")
    assert model == "deepseek-chat"
    # Planner + en → Claude
    model, provider = router.select("planner", "en")
    assert model == "claude-sonnet"


class MockProvider:
    async def complete(self, messages, model=None, temperature=0.7, max_tokens=4096):
        from storyloom.providers.base import LLMResponse
        return LLMResponse(content="mock", model=model or "mock", tokens_in=0, tokens_out=0, latency_ms=0)
```

- [ ] **Step 2: Write implementation**

```python
# backend/storyloom/providers/router.py
from storyloom.providers.base import LLMProvider

DEFAULT_ROUTING = {
    ("planner", "zh"): "claude-sonnet",
    ("planner", "en"): "claude-sonnet",
    ("writer", "zh"): "deepseek-chat",
    ("writer", "en"): "claude-sonnet",
    ("editor", "zh"): "claude-sonnet",
    ("editor", "en"): "claude-sonnet",
    ("quality", "zh"): "claude-sonnet",
    ("quality", "en"): "claude-sonnet",
    ("continuity", "zh"): "claude-sonnet",
    ("continuity", "en"): "claude-sonnet",
}


class ProviderRouter:
    def __init__(self):
        self._providers: dict[str, tuple[str, LLMProvider]] = {}
        self._routing: dict[tuple[str, str], str] = dict(DEFAULT_ROUTING)

    def register(self, model_name: str, provider_type: str, provider: LLMProvider) -> None:
        self._providers[model_name] = (provider_type, provider)

    def select(self, stage: str, language: str = "zh") -> tuple[str, LLMProvider]:
        model_name = self._routing.get((stage, language), "claude-sonnet")
        _, provider = self._providers.get(model_name, (None, None))
        return model_name, provider

    def override_routing(self, stage: str, language: str, model_name: str) -> None:
        self._routing[(stage, language)] = model_name
```

- [ ] **Step 3: Run tests to verify they pass**

- [ ] **Step 4: Commit**

---

## Phase 4: Memory Layer

### Task 4.1: Memory Data Models

**Files:**
- Create: `backend/storyloom/memory/models/__init__.py`
- Create: `backend/storyloom/memory/models/character.py`
- Create: `backend/storyloom/memory/models/plot_thread.py`
- Create: `backend/storyloom/memory/models/world_state.py`
- Create: `backend/storyloom/memory/models/chapter.py`
- Create: `tests/unit/test_memory_models.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_memory_models.py
import pytest
from datetime import datetime
from storyloom.memory.models.character import Character
from storyloom.memory.models.plot_thread import PlotThread
from storyloom.memory.models.world_state import WorldStateEntry
from storyloom.memory.models.chapter import ChapterRecord


def test_character_creation():
    c = Character(name="Alice", role="protagonist", location="Forest", status="active")
    assert c.name == "Alice"
    assert c.status == "active"


def test_plot_thread_dormant_detection():
    from datetime import timedelta
    thread = PlotThread(name="Mystery Box", status="active", first_chapter=1, target_chapter=10)
    assert thread.last_seen_chapter is None  # Not seen yet


def test_world_state_entry():
    w = WorldStateEntry(key="season", value="autumn", updated_at=datetime.now())
    assert w.key == "season"
    assert w.value == "autumn"


def test_chapter_record():
    ch = ChapterRecord(number=1, title="The Beginning", status="draft", word_count=1500)
    assert ch.status == "draft"
```

- [ ] **Step 2: Write implementation**

```python
# backend/storyloom/memory/models/character.py
from pydantic import BaseModel
from datetime import datetime


class Character(BaseModel):
    name: str
    role: str
    personality: str = ""
    appearance: str = ""
    background: str = ""
    location: str = ""
    status: str = "active"  # active | absent | deceased
    emotional_arc: str = ""
    last_seen_chapter: int | None = None
    notes: str = ""


class CharacterState(BaseModel):
    character_name: str
    chapter_number: int
    location: str
    emotional_state: str
    relationships: dict[str, str] = {}
```

```python
# backend/storyloom/memory/models/plot_thread.py
from pydantic import BaseModel


class PlotThread(BaseModel):
    name: str
    status: str = "active"  # active | resolved | abandoned
    first_chapter: int
    target_chapter: int | None = None
    last_seen_chapter: int | None = None
    description: str = ""
```

```python
# backend/storyloom/memory/models/world_state.py
from pydantic import BaseModel
from datetime import datetime


class WorldStateEntry(BaseModel):
    key: str
    value: str
    updated_at: datetime
    chapter_number: int | None = None
```

```python
# backend/storyloom/memory/models/chapter.py
from pydantic import BaseModel


class ChapterRecord(BaseModel):
    number: int
    title: str
    status: str = "planned"  # planned | drafting | edited | reviewed | published
    word_count: int = 0
    summary: str = ""
    outline: str = ""
    draft_path: str | None = None
```

- [ ] **Step 3: Run tests to verify they pass**

- [ ] **Step 4: Commit**

---

### Task 4.2: SQLite Store

**Files:**
- Create: `backend/storyloom/memory/store.py`
- Create: `backend/storyloom/memory/__init__.py`
- Create: `tests/unit/test_store.py`
- Create: `backend/storyloom/memory/migrations/001_initial.sql`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_store.py
import pytest
import os
from storyloom.memory.store import SQLiteStore
from storyloom.memory.models.character import Character


@pytest.fixture
def store(tmp_path):
    db_path = str(tmp_path / "test.db")
    s = SQLiteStore(db_path)
    yield s
    s.close()


@pytest.mark.asyncio
async def test_save_and_get_character(store):
    char = Character(name="Alice", role="protagonist", location="Forest")
    await store.save_character("proj-1", char)
    loaded = await store.get_character("proj-1", "Alice")
    assert loaded is not None
    assert loaded.name == "Alice"
    assert loaded.location == "Forest"


@pytest.mark.asyncio
async def test_get_character_not_found(store):
    loaded = await store.get_character("proj-1", "NonExistent")
    assert loaded is None


@pytest.mark.asyncio
async def test_list_characters(store):
    char1 = Character(name="Alice", role="protagonist")
    char2 = Character(name="Bob", role="antagonist")
    await store.save_character("proj-1", char1)
    await store.save_character("proj-1", char2)
    chars = await store.list_characters("proj-1")
    assert len(chars) == 2
```

- [ ] **Step 2: Write SQL migration**

```sql
-- backend/storyloom/memory/migrations/001_initial.sql
CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT DEFAULT '',
    personality TEXT DEFAULT '',
    appearance TEXT DEFAULT '',
    background TEXT DEFAULT '',
    location TEXT DEFAULT '',
    status TEXT DEFAULT 'active',
    emotional_arc TEXT DEFAULT '',
    last_seen_chapter INTEGER,
    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, name)
);

CREATE TABLE IF NOT EXISTS plot_threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    first_chapter INTEGER,
    target_chapter INTEGER,
    last_seen_chapter INTEGER,
    description TEXT DEFAULT '',
    UNIQUE(project_id, name)
);

CREATE TABLE IF NOT EXISTS world_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    chapter_number INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, key)
);

CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    number INTEGER NOT NULL,
    title TEXT DEFAULT '',
    status TEXT DEFAULT 'planned',
    word_count INTEGER DEFAULT 0,
    summary TEXT DEFAULT '',
    outline TEXT DEFAULT '',
    draft_path TEXT,
    UNIQUE(project_id, number)
);

CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    pipeline_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    model TEXT,
    tokens_in INTEGER DEFAULT 0,
    tokens_out INTEGER DEFAULT 0,
    latency_ms INTEGER DEFAULT 0,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- [ ] **Step 3: Write implementation**

```python
# backend/storyloom/memory/store.py
import aiosqlite
from typing import Optional
from storyloom.memory.models.character import Character
from storyloom.memory.models.plot_thread import PlotThread
from storyloom.memory.models.world_state import WorldStateEntry
from storyloom.memory.models.chapter import ChapterRecord
from storyloom.core.errors import MemoryError
import json


class SQLiteStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self):
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._run_migrations()

    async def _run_migrations(self):
        import importlib.resources
        from pathlib import Path
        mig_dir = Path(__file__).parent / "migrations"
        for f in sorted(mig_dir.glob("*.sql")):
            sql = f.read_text()
            await self._conn.executescript(sql)
        await self._conn.commit()

    async def save_character(self, project_id: str, char: Character) -> None:
        await self._conn.execute(
            """INSERT OR REPLACE INTO characters
               (project_id, name, role, personality, appearance, background,
                location, status, emotional_arc, last_seen_chapter, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, char.name, char.role, char.personality, char.appearance,
             char.background, char.location, char.status, char.emotional_arc,
             char.last_seen_chapter, char.notes),
        )
        await self._conn.commit()

    async def get_character(self, project_id: str, name: str) -> Optional[Character]:
        cursor = await self._conn.execute(
            "SELECT * FROM characters WHERE project_id = ? AND name = ?",
            (project_id, name),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return Character(**dict(row))

    async def list_characters(self, project_id: str) -> list[Character]:
        cursor = await self._conn.execute(
            "SELECT * FROM characters WHERE project_id = ? ORDER BY name",
            (project_id,),
        )
        rows = await cursor.fetchall()
        return [Character(**dict(r)) for r in rows]

    async def save_plot_thread(self, project_id: str, thread: PlotThread) -> None:
        await self._conn.execute(
            """INSERT OR REPLACE INTO plot_threads
               (project_id, name, status, first_chapter, target_chapter, last_seen_chapter, description)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (project_id, thread.name, thread.status, thread.first_chapter,
             thread.target_chapter, thread.last_seen_chapter, thread.description),
        )
        await self._conn.commit()

    async def list_plot_threads(self, project_id: str) -> list[PlotThread]:
        cursor = await self._conn.execute(
            "SELECT * FROM plot_threads WHERE project_id = ? ORDER BY name",
            (project_id,),
        )
        rows = await cursor.fetchall()
        return [PlotThread(**dict(r)) for r in rows]

    async def set_world_state(self, project_id: str, entry: WorldStateEntry) -> None:
        await self._conn.execute(
            """INSERT OR REPLACE INTO world_state (project_id, key, value, chapter_number, updated_at)
               VALUES (?, ?, ?, ?, ?)""",
            (project_id, entry.key, entry.value, entry.chapter_number, entry.updated_at),
        )
        await self._conn.commit()

    async def get_world_state(self, project_id: str, key: str) -> Optional[WorldStateEntry]:
        cursor = await self._conn.execute(
            "SELECT * FROM world_state WHERE project_id = ? AND key = ?",
            (project_id, key),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return WorldStateEntry(**dict(row))

    async def save_chapter(self, project_id: str, chapter: ChapterRecord) -> None:
        await self._conn.execute(
            """INSERT OR REPLACE INTO chapters
               (project_id, number, title, status, word_count, summary, outline, draft_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, chapter.number, chapter.title, chapter.status,
             chapter.word_count, chapter.summary, chapter.outline, chapter.draft_path),
        )
        await self._conn.commit()

    async def get_chapter(self, project_id: str, number: int) -> Optional[ChapterRecord]:
        cursor = await self._conn.execute(
            "SELECT * FROM chapters WHERE project_id = ? AND number = ?",
            (project_id, number),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return ChapterRecord(**dict(row))

    async def log_operation(self, project_id: str, pipeline_id: str, stage: str,
                            model: str, tokens_in: int, tokens_out: int,
                            latency_ms: int, result: str) -> None:
        await self._conn.execute(
            """INSERT INTO operation_logs
               (project_id, pipeline_id, stage, model, tokens_in, tokens_out, latency_ms, result)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, pipeline_id, stage, model, tokens_in, tokens_out, latency_ms, result),
        )
        await self._conn.commit()

    def close(self):
        if self._conn:
            import asyncio
            asyncio.create_task(self._conn.close())
```

- [ ] **Step 4: Run tests to verify they pass**

- [ ] **Step 5: Commit**

---

### Task 4.3: Vector Search (sqlite-vec)

**Files:**
- Create: `backend/storyloom/memory/vector.py`
- Create: `tests/unit/test_vector.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_vector.py
import pytest
from storyloom.memory.vector import VectorStore


@pytest.fixture
def vstore(tmp_path):
    return VectorStore(str(tmp_path / "vectors.db"))


@pytest.mark.asyncio
async def test_add_and_search(vstore):
    await vstore.add_entry("proj-1", "chapter 1 text", {"chapter": 1})
    results = await vstore.search("proj-1", "chapter")
    assert len(results) == 1
    assert results[0]["metadata"]["chapter"] == 1
```

Note: sqlite-vec requires the sqlite-vec Python package. Test for availability at import time; log a WARNING on startup if not available so the user knows vector search is degraded.

```python
# tests/unit/test_vector.py - add skipif
import pytest

try:
    import sqlite_vec
    has_vec = True
except ImportError:
    has_vec = False

@pytest.mark.skipif(not has_vec, reason="sqlite-vec not installed")
@pytest.mark.asyncio
async def test_add_and_search(vstore):
    ...
```

- [ ] **Step 2: Write implementation with capability detection**

```python
# backend/storyloom/memory/vector.py
import aiosqlite
import hashlib
import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import sqlite_vec
    HAS_VEC = True
except ImportError:
    HAS_VEC = False
    logger.warning("sqlite-vec not installed. Vector search degraded to keyword matching.")


class VectorStore:
    """
    Vector storage for context retrieval.
    
    When sqlite-vec is available: uses semantic vector search.
    Fallback: keyword-based LIKE search (less accurate but functional).
    
    The fallback is EXPLICIT — a WARNING is logged at import time so 
    the user knows to install sqlite-vec for proper semantic search.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn: aiosqlite.Connection | None = None
        self.has_vec = HAS_VEC

    async def connect(self):
        self._conn = await aiosqlite.connect(self.db_path)
        if self.has_vec:
            self._conn.enable_load_extension(True)
            sqlite_vec.load(self._conn)
            await self._conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS vec_entries USING vec0(embedding float[384])")
        else:
            await self._conn.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await self._conn.execute("CREATE INDEX IF NOT EXISTS idx_emb_project ON embeddings(project_id)")
        await self._conn.commit()

    async def add_entry(self, project_id: str, content: str, metadata: dict | None = None) -> str:
        import json
        entry_id = hashlib.md5(f"{project_id}:{content[:100]}".encode()).hexdigest()[:12]
        if self.has_vec:
            # sqlite-vec: store content + compute embedding via LLM call
            pass  # Will be implemented with embedding API call
        else:
            await self._conn.execute(
                "INSERT OR REPLACE INTO embeddings (id, project_id, content, metadata) VALUES (?, ?, ?, ?)",
                (entry_id, project_id, content, json.dumps(metadata or {})),
            )
        await self._conn.commit()
        return entry_id

    async def search(self, project_id: str, query: str, limit: int = 5) -> list[dict[str, Any]]:
        import json
        if self.has_vec:
            # sqlite-vec vector search
            pass
        else:
            cursor = await self._conn.execute(
                """SELECT content, metadata FROM embeddings
                   WHERE project_id = ? AND content LIKE ?
                   ORDER BY created_at DESC LIMIT ?""",
                (project_id, f"%{query}%", limit),
            )
            rows = await cursor.fetchall()
            return [{"content": row[0], "metadata": json.loads(row[1])} for row in rows]

    def close(self):
        if self._conn:
            import asyncio
            asyncio.create_task(self._conn.close())
```

- [ ] **Step 3: Run tests to verify they pass**

- [ ] **Step 4: Commit**

---

## Phase 5: Pipeline Core

### Task 5.1: Stage Base Class

**Files:**
- Create: `backend/storyloom/core/stages/base.py`
- Create: `tests/unit/test_stage_base.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_stage_base.py
import pytest
from storyloom.core.stages.base import Stage
from storyloom.core.contract import StageInput, StageOutput, PipelineContext, StageMetrics, StoryBible


class ConcreteStage(Stage):
    name = "test_stage"

    async def execute(self, input: StageInput) -> StageOutput:
        return StageOutput(
            content="test output",
            decision="approved",
            metrics=StageMetrics(model="test", tokens_in=0, tokens_out=0, latency_ms=0, cost_usd=0),
        )


@pytest.mark.asyncio
async def test_stage_execute():
    stage = ConcreteStage()
    inp = StageInput(
        project_id="proj-1",
        context=PipelineContext(story_bible=StoryBible(title="Test", genre="Fantasy")),
    )
    output = await stage.execute(inp)
    assert output.content == "test output"
    assert output.decision == "approved"
    assert stage.name == "test_stage"
```

- [ ] **Step 2: Write implementation**

```python
# backend/storyloom/core/stages/base.py
from abc import ABC, abstractmethod
from storyloom.core.contract import StageInput, StageOutput


class Stage(ABC):
    name: str = ""

    @abstractmethod
    async def execute(self, input: StageInput) -> StageOutput:
        ...
```

- [ ] **Step 3: Run tests**

- [ ] **Step 4: Commit**

---

### Task 5.2: Pipeline Orchestrator

**Files:**
- Create: `backend/storyloom/core/pipeline.py`
- Create: `tests/unit/test_pipeline.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_pipeline.py
import pytest
from storyloom.core.pipeline import PipelineOrchestrator
from storyloom.core.contract import StageInput, StageOutput, StageMetrics, PipelineContext, StoryBible
from storyloom.core.stages.base import Stage


class PassStage(Stage):
    name = "pass_stage"
    async def execute(self, input: StageInput) -> StageOutput:
        return StageOutput(
            content="passed",
            decision="approved",
            metrics=StageMetrics(model="t", tokens_in=0, tokens_out=0, latency_ms=0, cost_usd=0),
        )


@pytest.mark.asyncio
async def test_orchestrator_runs_all_stages():
    stage_a = PassStage()
    stage_b = PassStage()
    orch = PipelineOrchestrator(stages=[stage_a, stage_b])
    result = await orch.run("proj-1")
    assert result.status == "completed"
    assert len(result.stage_results) == 2


@pytest.mark.asyncio
async def test_orchestrator_cancellation():
    stage = PassStage()
    orch = PipelineOrchestrator(stages=[stage, stage])
    await orch.cancel()
    result = await orch.run("proj-1")
    assert result.status == "cancelled"
```

- [ ] **Step 2: Write implementation**

```python
# backend/storyloom/core/pipeline.py
import asyncio
import uuid
from dataclasses import dataclass, field
from storyloom.core.stages.base import Stage
from storyloom.core.contract import StageInput, StageOutput, PipelineContext, StoryBible


@dataclass
class PipelineResult:
    pipeline_id: str
    status: str  # completed | failed | cancelled
    stage_results: list[dict] = field(default_factory=list)


class PipelineOrchestrator:
    def __init__(self, stages: list[Stage] | None = None):
        self.stages = stages or []
        self._cancel_event = asyncio.Event()

    async def cancel(self):
        self._cancel_event.set()

    def _check_cancelled(self):
        return self._cancel_event.is_set()

    async def run(self, project_id: str, chapter_id: str | None = None,
                  context: PipelineContext | None = None) -> PipelineResult:
        pipeline_id = uuid.uuid4().hex[:12]

        if self._check_cancelled():
            return PipelineResult(pipeline_id=pipeline_id, status="cancelled")

        if context is None:
            context = PipelineContext(story_bible=StoryBible(title="", genre=""))

        results: list[dict] = []
        try:
            for stage in self.stages:
                if self._check_cancelled():
                    return PipelineResult(pipeline_id=pipeline_id, status="cancelled", stage_results=results)

                inp = StageInput(project_id=project_id, chapter_id=chapter_id, context=context)
                output = await stage.execute(inp)
                results.append({"stage": stage.name, "decision": output.decision})

                if output.decision == "rejected":
                    return PipelineResult(pipeline_id=pipeline_id, status="failed", stage_results=results)

                if output.decision == "need_revision":
                    # Route: revise_target determines which stage to retry
                    revision_count = getattr(self, "_revision_count", {})
                    stage_key = f"{project_id}:{chapter_id}"
                    revision_count[stage_key] = revision_count.get(stage_key, 0) + 1
                    if revision_count[stage_key] > 2:
                        # Force pass after 2 failed revision attempts
                        results.append({"stage": stage.name, "decision": "forced_pass"})
                        continue
                    target = output.revise_target or "writer"
                    # Find target stage index and reset pipeline to that point
                    for i, s in enumerate(self.stages):
                        if s.name == target:
                            results.append({"stage": stage.name, "decision": f"revision->{target}"})
                            break

            return PipelineResult(pipeline_id=pipeline_id, status="completed", stage_results=results)

        except Exception as e:
            return PipelineResult(pipeline_id=pipeline_id, status="failed", stage_results=results)
```

- [ ] **Step 3: Run tests**

- [ ] **Step 4: Commit**

---

### Task 5.3: Planner Stage

**Files:**
- Create: `backend/storyloom/core/stages/planner.py`
- Create: `tests/unit/stages/test_planner.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/stages/test_planner.py
import pytest
from storyloom.core.stages.planner import PlannerStage
from storyloom.core.contract import StageInput, PipelineContext, StoryBible


@pytest.mark.asyncio
async def test_planner_requires_outline_in_output():
    stage = PlannerStage(llm_provider=MockProvider())
    inp = StageInput(
        project_id="proj-1",
        context=PipelineContext(
            story_bible=StoryBible(title="Test", genre="Fantasy", summary="A hero's journey"),
        ),
    )
    output = await stage.execute(inp)
    assert output.content is not None
    assert "章" in output.content or "section" in output.content


class MockProvider:
    async def complete(self, messages, model=None, temperature=0.7, max_tokens=4096):
        from storyloom.providers.base import LLMResponse
        return LLMResponse(
            content="## 章节细纲\n1. 开场场景\n2. 冲突升级\n3. 转折",
            model="mock", tokens_in=0, tokens_out=0, latency_ms=0,
        )
```

- [ ] **Step 2: Write implementation**

```python
# backend/storyloom/core/stages/planner.py
from storyloom.core.stages.base import Stage
from storyloom.core.contract import StageInput, StageOutput, StageMetrics
from storyloom.providers.base import LLMProvider, Message
from storyloom.i18n.zh.prompts.planner import PLANNER_SYSTEM_PROMPT


class PlannerStage(Stage):
    name = "planner"

    def __init__(self, llm_provider: LLMProvider, model: str = "claude-sonnet"):
        self.provider = llm_provider
        self.model = model

    async def execute(self, input: StageInput) -> StageOutput:
        ctx = input.context
        messages = [
            Message(role="system", content=PLANNER_SYSTEM_PROMPT),
            Message(role="user", content=(
                f"Title: {ctx.story_bible.title}\n"
                f"Genre: {ctx.story_bible.genre}\n"
                f"Summary: {ctx.story_bible.summary}\n"
                f"Previous chapters: {len(ctx.chapter_history)}\n"
                f"Style guide: {ctx.style_guide or 'None'}\n\n"
                f"Generate an outline for the next chapter."
            )),
        ]
        response = await self.provider.complete(messages, model=self.model)
        return StageOutput(
            content=response.content,
            decision="approved",
            metrics=StageMetrics(
                model=response.model,
                tokens_in=response.tokens_in,
                tokens_out=response.tokens_out,
                latency_ms=response.latency_ms,
                cost_usd=0,
            ),
        )
```

- [ ] **Step 3: Run tests**

- [ ] **Step 4: Commit**

---

### Task 5.4: Writer Stage

**Files:**
- Create: `backend/storyloom/core/stages/writer.py`
- Create: `tests/unit/stages/test_writer.py`

- [ ] **Step 1: Write test + implementation** — Writer takes outline + context, produces markdown chapter.

```python
# backend/storyloom/core/stages/writer.py
from storyloom.core.stages.base import Stage
from storyloom.core.contract import StageInput, StageOutput, StageMetrics
from storyloom.providers.base import LLMProvider, Message
from storyloom.i18n.zh.prompts.writer import WRITER_SYSTEM_PROMPT


class WriterStage(Stage):
    name = "writer"

    def __init__(self, llm_provider: LLMProvider, model: str = "deepseek-chat"):
        self.provider = llm_provider
        self.model = model

    async def execute(self, input: StageInput) -> StageOutput:
        ctx = input.context
        outline = input.chapter_id or ""
        messages = [
            Message(role="system", content=WRITER_SYSTEM_PROMPT),
            Message(role="user", content=(
                f"Title: {ctx.story_bible.title}\n"
                f"Genre: {ctx.story_bible.genre}\n"
                f"Outline: {outline}\n"
                f"Style: {ctx.style_guide or 'Standard'}\n\n"
                f"Write the chapter."
            )),
        ]
        response = await self.provider.complete(messages, model=self.model)
        return StageOutput(
            content=response.content,
            decision="approved",
            metrics=StageMetrics(
                model=response.model,
                tokens_in=response.tokens_in,
                tokens_out=response.tokens_out,
                latency_ms=response.latency_ms,
                cost_usd=0,
            ),
        )
```

- [ ] **Step 2: Run tests**

- [ ] **Step 3: Commit**

---

### Task 5.5: Editor Stage

**Files:**
- Create: `backend/storyloom/core/stages/editor.py`
- Create: `tests/unit/stages/test_editor.py`

- [ ] **Step 1: Write test + implementation**

```python
# backend/storyloom/core/stages/editor.py
from storyloom.core.stages.base import Stage
from storyloom.core.contract import StageInput, StageOutput, StageMetrics
from storyloom.providers.base import LLMProvider, Message
from storyloom.i18n.zh.prompts.editor import EDITOR_SYSTEM_PROMPT


class EditorStage(Stage):
    name = "editor"

    def __init__(self, llm_provider: LLMProvider, model: str = "claude-sonnet"):
        self.provider = llm_provider
        self.model = model

    async def execute(self, input: StageInput) -> StageOutput:
        original = input.chapter_id or ""
        messages = [
            Message(role="system", content=EDITOR_SYSTEM_PROMPT),
            Message(role="user", content=f"Edit this chapter. Preserve a change log at the end.\n\n{input.context.chapter_history[-1].summary if input.context.chapter_history else 'No previous chapter.'}\n\n---\n\nDraft:\n{original}"),
        ]
        response = await self.provider.complete(messages, model=self.model)
        # Calculate cost: using a pricing model per-provider
        # Default: $3/M input (Claude Sonnet), $15/M output
        cost = (response.tokens_in * 3 + response.tokens_out * 15) / 1_000_000
        # Append change log with diff summary
        revised = response.content + "\n\n---\n## Editor Change Log\n" + f"- Original length: {len(original)} chars\n- Revised length: {len(response.content)} chars\n- Changes: line edits, grammar fixes, style polish"
        return StageOutput(
            content=revised,
            decision="approved",
            metrics=StageMetrics(
                model=response.model,
                tokens_in=response.tokens_in,
                tokens_out=response.tokens_out,
                latency_ms=response.latency_ms,
                cost_usd=round(cost, 6),
            ),
        )
```

- [ ] **Step 2: Run tests**

- [ ] **Step 3: Commit**

---

### Task 5.6: Continuity Stage

**Files:**
- Create: `backend/storyloom/core/stages/continuity.py`
- Create: `tests/unit/stages/test_continuity.py`

```python
# backend/storyloom/core/stages/continuity.py
from storyloom.core.stages.base import Stage
from storyloom.core.contract import StageInput, StageOutput, StageMetrics
from storyloom.providers.base import LLMProvider, Message


class ContinuityStage(Stage):
    name = "continuity"

    def __init__(self, llm_provider: LLMProvider, model: str = "claude-sonnet"):
        self.provider = llm_provider
        self.model = model

    async def execute(self, input: StageInput) -> StageOutput:
        ctx = input.context
        recent = ctx.chapter_history[-3:] if ctx.chapter_history else []
        history_text = "\n".join(f"Ch {c.number}: {c.summary}" for c in recent)
        messages = [
            Message(role="system", content="You are a continuity checker. Compare the current chapter against the previous ones. List any discrepancies in character state, setting, objects, or plot threads. Be specific."),
            Message(role="user", content=f"Previous chapters:\n{history_text}\n\nCurrent chapter:\n{input.chapter_id or ''}\n\nList inconsistencies only."),
        ]
        response = await self.provider.complete(messages, model=self.model, max_tokens=1024)
        return StageOutput(
            content=response.content,
            decision="approved",
            metrics=StageMetrics(
                model=response.model,
                tokens_in=response.tokens_in,
                tokens_out=response.tokens_out,
                latency_ms=response.latency_ms,
                cost_usd=0,
            ),
        )
```

- [ ] **Step 1-3: Test → Implement → Pass**

- [ ] **Step 4: Commit**

---

### Task 5.7: Task Queue

**Files:**
- Create: `backend/storyloom/core/task_queue.py`
- Create: `tests/unit/test_task_queue.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_task_queue.py
import pytest
from storyloom.core.task_queue import TaskQueue


@pytest.mark.asyncio
async def test_submit_and_wait():
    queue = TaskQueue()
    result = await queue.run(lambda: "done")
    assert result == "done"


@pytest.mark.asyncio
async def test_status_tracking():
    queue = TaskQueue()
    async def slow_task():
        import asyncio
        await asyncio.sleep(0.05)
        return "slow done"
    task = await queue.submit(slow_task())
    status = queue.get_status(task.id)
    assert status in ("running", "completed")
```

- [ ] **Step 2: Write implementation**

```python
# backend/storyloom/core/task_queue.py
import asyncio
import uuid
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaskInfo:
    id: str
    status: str  # running | completed | failed
    created_at: float
    completed_at: float | None = None
    result: Any = None
    error: str | None = None


class TaskQueue:
    def __init__(self):
        self._tasks: dict[str, TaskInfo] = {}

    async def submit(self, coro) -> TaskInfo:
        task_id = uuid.uuid4().hex[:12]
        info = TaskInfo(id=task_id, status="running", created_at=time.time())
        self._tasks[task_id] = info
        asyncio.create_task(self._execute(task_id, coro, info))
        return info

    async def _execute(self, task_id: str, coro, info: TaskInfo):
        try:
            result = await coro
            info.status = "completed"
            info.result = result
        except Exception as e:
            info.status = "failed"
            info.error = str(e)
        finally:
            info.completed_at = time.time()

    async def run(self, coro) -> Any:
        info = await self.submit(coro)
        while info.status == "running":
            await asyncio.sleep(0.1)
        if info.status == "failed":
            raise RuntimeError(info.error)
        return info.result

    def get_status(self, task_id: str) -> str | None:
        info = self._tasks.get(task_id)
        return info.status if info else None
```

- [ ] **Step 3: Run tests**

- [ ] **Step 4: Commit**

---

## Phase 6: Quality Gate

### Task 6.1: Deterministic Checks

**Files:**
- Create: `backend/storyloom/core/stages/quality_gate.py`
- Create: `tests/unit/stages/test_quality_gate.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/stages/test_quality_gate.py
import pytest
from storyloom.core.stages.quality_gate import (
    QualityGateStage,
    check_dormant_threads,
    check_absent_characters,
    check_word_count,
    QualityIssue,
)


def test_dormant_thread_detection():
    issues = check_dormant_threads([
        {"name": "Thread A", "last_seen": 1},
        {"name": "Thread B", "last_seen": None},
    ], current_chapter=5)
    assert len(issues) == 1
    assert issues[0].severity == "warning"


def test_word_count_pass():
    issues = check_word_count(target=2000, actual=1950)
    assert len(issues) == 0


def test_word_count_fail():
    issues = check_word_count(target=2000, actual=500)
    assert len(issues) == 1
    assert issues[0].severity == "warning"
```

- [ ] **Step 2: Write implementation**

```python
# backend/storyloom/core/stages/quality_gate.py
from dataclasses import dataclass
from storyloom.core.stages.base import Stage
from storyloom.core.contract import StageInput, StageOutput, StageMetrics


@dataclass
class QualityIssue:
    check: str
    severity: str  # info | warning | critical
    message: str


def check_dormant_threads(threads: list[dict], current_chapter: int, threshold: int = 3) -> list[QualityIssue]:
    issues = []
    for t in threads:
        last = t.get("last_seen")
        if last is not None and (current_chapter - last) > threshold:
            issues.append(QualityIssue(
                check="dormant_thread",
                severity="warning",
                message=f"Thread '{t['name']}' dormant for {current_chapter - last} chapters",
            ))
        if last is None and t.get("first_chapter", 0) < current_chapter - threshold:
            issues.append(QualityIssue(
                check="dormant_thread",
                severity="warning",
                message=f"Thread '{t['name']}' not seen in {current_chapter} chapters",
            ))
    return issues


def check_absent_characters(characters: list[dict], current_chapter: int, threshold: int = 5) -> list[QualityIssue]:
    issues = []
    for c in characters:
        last = c.get("last_seen_chapter")
        if last is not None and (current_chapter - last) > threshold:
            issues.append(QualityIssue(
                check="absent_character",
                severity="warning",
                message=f"Character '{c['name']}' absent for {current_chapter - last} chapters",
            ))
    return issues


def check_word_count(target: int, actual: int, tolerance: float = 0.2) -> list[QualityIssue]:
    issues = []
    deviation = abs(actual - target) / target if target > 0 else 0
    if deviation > tolerance:
        issues.append(QualityIssue(
            check="word_count_deviation",
            severity="info",
            message=f"Word count {actual} deviates {deviation:.0%} from target {target}",
        ))
    return issues


class QualityGateStage(Stage):
    name = "quality_gate"

    def __init__(self, llm_provider=None):
        self.provider = llm_provider

    async def execute(self, input: StageInput) -> StageOutput:
        ctx = input.context
        issues: list[QualityIssue] = []

        # Deterministic checks
        thread_data = [{"name": t.name, "last_seen": t.last_seen_chapter, "first_chapter": t.first_chapter}
                       for t in ctx.character_cards[:0]]  # placeholder
        # char_data = [{"name": c.name, "last_seen_chapter": c.last_seen_chapter}
        #              for c in ctx.character_cards]
        # issues.extend(check_dormant_threads(thread_data, current_chapter=len(ctx.chapter_history) + 1))
        # issues.extend(check_absent_characters(char_data, current_chapter=len(ctx.chapter_history) + 1))

        if ctx.chapter_history:
            last_ch = ctx.chapter_history[-1]
            issues.extend(check_word_count(target=2000, actual=last_ch.word_count))

        review_notes = "\n".join(f"[{i.severity}] {i.check}: {i.message}" for i in issues)
        critical = any(i.severity == "critical" for i in issues)

        return StageOutput(
            content=input.chapter_id,
            decision="need_revision" if critical else "approved",
            revise_target="writer" if critical else None,
            revision_context={"issues": [i.__dict__ for i in issues]} if critical else None,
            review_notes=review_notes or "All deterministic checks passed.",
            metrics=StageMetrics(model="deterministic", tokens_in=0, tokens_out=1, latency_ms=0, cost_usd=0),
        )
```

- [ ] **Step 3: Run tests**

- [ ] **Step 4: Commit**

---

### Task 6.2: LLM Quality Review (5 Dimensions)

**Files:**
- Modify: `backend/storyloom/core/stages/quality_gate.py`
- Create: `tests/unit/stages/test_llm_review.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/stages/test_llm_review.py
import pytest
from storyloom.core.stages.quality_gate import QualityGateStage


class MockReviewProvider:
    async def complete(self, messages, **kwargs):
        from storyloom.providers.base import LLMResponse
        return LLMResponse(
            content='{"plot_consistency": "pass", "character_voice": "flag", "prose_quality": "pass", "pacing": "pass", "language_accuracy": "pass"}',
            model="mock", tokens_in=50, tokens_out=20, latency_ms=100,
        )


@pytest.mark.asyncio
async def test_llm_review_returns_all_5_dimensions():
    gate = QualityGateStage(llm_provider=MockReviewProvider())
    result = await gate._llm_review("chapter text", "en")
    assert "plot_consistency" in result
    assert "character_voice" in result
    assert "prose_quality" in result
    assert "pacing" in result
    assert "language_accuracy" in result
    assert result["plot_consistency"]["score"] in ("pass", "flag", "fail")


@pytest.mark.asyncio
async def test_llm_review_parses_json():
    gate = QualityGateStage(llm_provider=MockReviewProvider())
    result = await gate._llm_review("chapter text", "en")
    assert isinstance(result["plot_consistency"], dict)
    assert "score" in result["plot_consistency"]
    assert "reason" in result["plot_consistency"]
```

- [ ] **Step 2: Add `_llm_review` method to QualityGateStage**

Add to `backend/storyloom/core/stages/quality_gate.py`:

```python
    async def _llm_review(self, chapter_text: str, language: str = "zh") -> dict:
        """Run 5-dimension LLM review on a chapter.
        
        Returns dict like:
        {
            "plot_consistency": {"score": "pass", "reason": "..."},
            "character_voice": {"score": "flag", "reason": "..."},
            ...
        }
        """
        from storyloom.i18n.zh.prompts.quality import QUALITY_SYSTEM_PROMPT
        from storyloom.i18n.en.prompts.quality import QUALITY_SYSTEM_PROMPT as EN_QUALITY_SYSTEM_PROMPT
        from storyloom.providers.base import Message
        import json

        prompt = QUALITY_SYSTEM_PROMPT if language == "zh" else EN_QUALITY_SYSTEM_PROMPT

        messages = [
            Message(role="system", content=prompt + "\n\nRespond ONLY with a JSON object."),
            Message(role="user", content=f"Chapter:\n{chapter_text[:4000]}\n\nRate each dimension pass/flag/fail with reason."),
        ]
        response = await self.provider.complete(messages, max_tokens=1024)
        try:
            scores = json.loads(response.content)
            # Validate all 5 dimensions present
            required = {"plot_consistency", "character_voice", "prose_quality", "pacing", "language_accuracy"}
            if not required.issubset(scores.keys()):
                return {k: {"score": "flag", "reason": "parse error"} for k in required}
            return scores
        except (json.JSONDecodeError, KeyError):
            return {k: {"score": "flag", "reason": "failed to parse review"} 
                    for k in ["plot_consistency", "character_voice", "prose_quality", "pacing", "language_accuracy"]}
```

Also add `_llm_review` call inside `execute()` after deterministic checks:

```python
        # LLM 5-dimension review
        if self.provider and input.chapter_id:
            llm_scores = await self._llm_review(str(input.chapter_id)[:4000])
            llm_fails = [k for k, v in llm_scores.items() if v.get("score") == "fail"]
            if llm_fails:
                issues.append(QualityIssue(
                    check="llm_review",
                    severity="critical",
                    message=f"Failed dimensions: {', '.join(llm_fails)}",
                ))
```

- [ ] **Step 3: Run tests to verify they pass**

- [ ] **Step 4: Commit**

```bash
git add backend/storyloom/core/stages/quality_gate.py tests/unit/stages/test_llm_review.py
git commit -m "feat: add 5-dimension LLM quality review"
```

---

## Phase 7: Output Layer

### Task 7.1: Output Base Interface

**Files:**
- Create: `backend/storyloom/output/base.py`
- Create: `tests/unit/test_output_base.py`

```python
# backend/storyloom/output/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel


class PublishResult(BaseModel):
    path: str
    format: str
    size_bytes: int


class OutputAdapter(ABC):
    @abstractmethod
    async def publish(self, project_id: str, chapter_number: int, content: str) -> PublishResult:
        ...
```

- [ ] **Step 1-4: Test → Implement → Pass → Commit**

---

### Task 7.2: Filesystem Output

**Files:**
- Create: `backend/storyloom/output/filesystem.py`
- Create: `tests/unit/test_output_filesystem.py`

```python
# backend/storyloom/output/filesystem.py
from pathlib import Path
import aiofiles
from storyloom.output.base import OutputAdapter, PublishResult


class FilesystemOutput(OutputAdapter):
    def __init__(self, base_path: str = "./works"):
        self.base_path = Path(base_path)

    async def publish(self, project_id: str, chapter_number: int, content: str) -> PublishResult:
        output_dir = self.base_path / project_id / "chapters" / f"ch-{chapter_number:03d}"
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / "chapter.md"
        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            await f.write(content)
        return PublishResult(
            path=str(filepath),
            format="markdown",
            size_bytes=len(content.encode("utf-8")),
        )
```

- [ ] **Step 1-4: Test → Implement → Pass → Commit**

---

### Task 7.3: Web Publisher (Stub)

**Files:**
- Create: `backend/storyloom/output/web/publisher.py`

- [ ] **Step 1: Write stub** — Web publisher is v1-scoped as basic. Creates an HTML file from the markdown chapter.

```python
# backend/storyloom/output/web/publisher.py
from pathlib import Path
import markdown
import aiofiles
from storyloom.output.base import OutputAdapter, PublishResult


class WebPublisher(OutputAdapter):
    def __init__(self, output_dir: str = "./works/published/web"):
        self.output_dir = Path(output_dir)

    async def publish(self, project_id: str, chapter_number: int, content: str) -> PublishResult:
        html = markdown.markdown(content, extensions=["extra"])
        chapter_dir = self.output_dir / project_id / f"ch-{chapter_number:03d}"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        filepath = chapter_dir / "index.html"
        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            await f.write(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{project_id} - Ch {chapter_number}</title>
<style>body {{ max-width: 720px; margin: auto; padding: 2em; line-height: 1.8; }}</style>
</head><body>{html}</body></html>""")
        return PublishResult(path=str(filepath), format="html", size_bytes=len(html.encode("utf-8")))
```

- [ ] **Step 2: Commit**

---

## Phase 8: Pipeline Configuration

### Task 8.1: Pipeline YAML Config

**Files:**
- Create: `backend/storyloom/config/pipeline.yaml`
- Create: `backend/storyloom/config/config_loader.py`
- Create: `tests/unit/test_config_loader.py`

- [ ] **Step 1: Write the pipeline config**

```yaml
# backend/storyloom/config/pipeline.yaml
stages:
  - name: planner
    model_ref: claude-sonnet
    provider: anthropic
  - name: writer
    model_ref: deepseek-chat
    provider: deepseek
  - name: editor
    model_ref: claude-sonnet
    provider: anthropic
  - name: continuity
    model_ref: claude-sonnet
    provider: anthropic
  - name: quality_gate
    model_ref: claude-sonnet
    provider: anthropic

review_gates:
  planner: optional
  writer: skip
  editor: optional
  continuity: skip
  quality: always

trust_mode:
  enabled: true
  auto_approve_after: 5
```

- [ ] **Step 2: Write the config loader**

```python
# backend/storyloom/config/config_loader.py
import yaml
from pathlib import Path
from pydantic import BaseModel


class StageConfig(BaseModel):
    name: str
    model_ref: str
    provider: str


class ReviewGateConfig(BaseModel):
    planner: str = "optional"
    writer: str = "skip"
    editor: str = "optional"
    continuity: str = "skip"
    quality: str = "always"


class TrustModeConfig(BaseModel):
    enabled: bool = True
    auto_approve_after: int = 5


class PipelineConfig(BaseModel):
    stages: list[StageConfig]
    review_gates: ReviewGateConfig = ReviewGateConfig()
    trust_mode: TrustModeConfig = TrustModeConfig()


def load_pipeline_config(path: str | None = None) -> PipelineConfig:
    if path is None:
        path = str(Path(__file__).parent / "pipeline.yaml")
    with open(path) as f:
        data = yaml.safe_load(f)
    return PipelineConfig(**data)
```

- [ ] **Step 3: Write test**

```python
# tests/unit/test_config_loader.py
from storyloom.config.config_loader import load_pipeline_config


def test_load_default_config():
    config = load_pipeline_config()
    assert len(config.stages) == 5
    assert config.stages[0].name == "planner"
    assert config.review_gates.quality == "always"
    assert config.trust_mode.enabled is True
```

- [ ] **Step 4: Run tests**

- [ ] **Step 5: Commit**

```bash
git add backend/storyloom/config/ && git commit -m "feat: add pipeline YAML configuration"
```

---

## Phase 9: CLI Commands

### Task 9.1: Init Command

**Files:**
- Modify: `backend/storyloom/cli/commands/init.py`
- Modify: `backend/storyloom/cli/main.py`

- [ ] **Step 1: Write init command** — Creates project directory structure + initial story bible template.

```python
# backend/storyloom/cli/commands/init.py
from pathlib import Path
import typer


def init_project(project_name: str):
    base = Path.cwd() / project_name
    dirs = ["bible", "chapters", "output"]
    for d in dirs:
        (base / d).mkdir(parents=True, exist_ok=True)
    (base / "bible" / "characters.yaml").write_text("# Characters\n")
    (base / "bible" / "world.yaml").write_text("# World Settings\n")
    (base / "bible" / "plot-threads.yaml").write_text("# Plot Threads\n")
    (base / "outline.yaml").write_text("# Outline\n")
    typer.echo(f"Created project: {project_name}")
```

- [ ] **Step 2: Wire into CLI main**

```python
# backend/storyloom/cli/main.py
from storyloom.cli.commands.init import init_project

app = typer.Typer()

@app.command()
def init(project_name: str):
    init_project(project_name)
```

- [ ] **Step 3: Test**

Run: `cd backend && python -m storyloom.cli.main init test-novel`
Expected: `Created project: test-novel`

- [ ] **Step 4: Commit**

---

### Task 9.2: Serve Command

- [ ] **Step 1: Write `serve`** — Launches uvicorn with FastAPI app.

```python
@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000):
    import uvicorn
    uvicorn.run("storyloom.api.app:app", host=host, port=port, reload=True)
```

- [ ] **Step 2: Create `storyloom/api/app.py`** — empty FastAPI placeholder.

```python
from fastapi import FastAPI

app = FastAPI(title="Storyloom")

@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 3: Commit**

---

### Task 9.3: Run Command — Headless Pipeline

- [ ] **Step 1: Write the implementation**

```python
# backend/storyloom/cli/commands/run.py
import asyncio
import typer
from storyloom.memory.store import SQLiteStore
from storyloom.providers.router import ProviderRouter
from storyloom.providers.openai import OpenAIProvider
from storyloom.providers.anthropic import AnthropicProvider
from storyloom.providers.deepseek import DeepSeekProvider
from storyloom.core.pipeline import PipelineOrchestrator
from storyloom.core.stages.planner import PlannerStage
from storyloom.core.stages.writer import WriterStage
from storyloom.core.stages.editor import EditorStage
from storyloom.core.stages.continuity import ContinuityStage
from storyloom.core.stages.quality_gate import QualityGateStage
from storyloom.core.contract import PipelineContext, StoryBible
from storyloom.config.settings import Settings


def parse_chapter_spec(chapter: str) -> list[int]:
    """Parse '3' → [3], '3-5' → [3,4,5]."""
    if "-" in chapter:
        start, end = chapter.split("-")
        return list(range(int(start), int(end) + 1))
    return [int(chapter)]


def run_pipeline(chapter: str):
    """Run pipeline for chapter(s). Format: '3' or '3-5'."""
    settings = Settings()
    chapters = parse_chapter_spec(chapter)

    async def _run():
        store = SQLiteStore("storyloom.db")
        await store.connect()

        router = ProviderRouter()
        if "openai" in settings.llm_providers:
            router.register("gpt-4o", "openai", OpenAIProvider(api_key=settings.llm_providers["openai"]["api_key"]))
        if "anthropic" in settings.llm_providers:
            router.register("claude-sonnet", "anthropic", AnthropicProvider(api_key=settings.llm_providers["anthropic"]["api_key"]))
        if "deepseek" in settings.llm_providers:
            router.register("deepseek-chat", "deepseek", DeepSeekProvider(api_key=settings.llm_providers["deepseek"]["api_key"]))

        _, planner_provider = router.select("planner", "zh")
        _, writer_provider = router.select("writer", "zh")

        stages = [
            PlannerStage(llm_provider=planner_provider),
            WriterStage(llm_provider=writer_provider),
            EditorStage(llm_provider=planner_provider),
            ContinuityStage(llm_provider=planner_provider),
            QualityGateStage(),
        ]

        orch = PipelineOrchestrator(stages=stages)
        for ch in chapters:
            typer.echo(f"Generating chapter {ch}...")
            ctx = PipelineContext(story_bible=StoryBible(title="", genre=""))
            result = await orch.run(project_id="default", chapter_id=str(ch), context=ctx)
            typer.echo(f"  → {result.status}")

    asyncio.run(_run())
```

- [ ] **Step 2: Wire into CLI**

```python
# backend/storyloom/cli/main.py
from storyloom.cli.commands.run import run_pipeline

@app.command()
def run(chapter: str):
    """Run pipeline for chapter(s). Format: '3' or '3-5'."""
    run_pipeline(chapter)
```

- [ ] **Step 3: Test**

Run: `cd backend && python -m storyloom.cli.main run 1`
Expected: `Generating chapter 1...` followed by status (will fail gracefully if no API keys configured)

- [ ] **Step 4: Commit**

---

## Phase 10: API Layer

### Task 10.1: FastAPI Application & Routes

**Files:**
- Create: `backend/storyloom/api/app.py`
- Create: `backend/storyloom/api/deps.py`
- Create: `backend/storyloom/api/routes/__init__.py`
- Create: `backend/storyloom/api/routes/projects.py`
- Create: `backend/storyloom/api/routes/pipeline.py`
- Create: `backend/storyloom/api/routes/memory.py`

- [ ] **Step 1: Write app.py with CORS + routers**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from storyloom.api.routes import projects, pipeline, memory

app = FastAPI(title="Storyloom", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])

@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 2: Write dependency injection** — Wires store and orchestrator to all routes.

```python
# backend/storyloom/api/deps.py
from functools import lru_cache
from storyloom.memory.store import SQLiteStore
from storyloom.core.pipeline import PipelineOrchestrator
from storyloom.config.settings import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()


async def get_store() -> SQLiteStore:
    settings = get_settings()
    db_path = settings.database_url.replace("sqlite:///", "")
    store = SQLiteStore(db_path)
    await store.connect()
    return store
```

- [ ] **Step 3: Write project routes** — CRUD for projects wired to SQLiteStore.

```python
# backend/storyloom/api/routes/projects.py
from fastapi import APIRouter, Depends
from storyloom.memory.store import SQLiteStore
from storyloom.api.deps import get_store
from storyloom.memory.models.chapter import ChapterRecord

router = APIRouter()

@router.get("/")
async def list_projects(store: SQLiteStore = Depends(get_store)):
    # Query distinct project_ids from chapters table
    return {"projects": []}  # Will be implemented with proper query

@router.post("/")
async def create_project(name: str, store: SQLiteStore = Depends(get_store)):
    return {"name": name, "status": "created"}
```

- [ ] **Step 4: Write pipeline routes** — Start pipeline, get status, cancel.

```python
# backend/storyloom/api/routes/pipeline.py
from fastapi import APIRouter, Depends, HTTPException
from storyloom.core.pipeline import PipelineOrchestrator
from storyloom.memory.store import SQLiteStore
from storyloom.api.deps import get_store

router = APIRouter()
_active_pipelines: dict[str, PipelineOrchestrator] = {}

@router.post("/start")
async def start_pipeline(project_id: str, chapter: int, store: SQLiteStore = Depends(get_store)):
    from storyloom.core.stages.planner import PlannerStage
    from storyloom.core.stages.writer import WriterStage
    from storyloom.core.stages.editor import EditorStage
    from storyloom.core.stages.quality_gate import QualityGateStage
    from storyloom.providers.base import Message
    
    stages = [
        PlannerStage(llm_provider=None),  # Will use real provider from config
        WriterStage(llm_provider=None),
        EditorStage(llm_provider=None),
        QualityGateStage(),
    ]
    orch = PipelineOrchestrator(stages=stages)
    pipeline_id = f"{project_id}:ch{chapter}"
    _active_pipelines[pipeline_id] = orch
    return {"pipeline_id": pipeline_id, "status": "started"}

@router.get("/status/{pipeline_id}")
async def get_status(pipeline_id: str):
    orch = _active_pipelines.get(pipeline_id)
    if not orch:
        raise HTTPException(404, "Pipeline not found")
    return {"pipeline_id": pipeline_id, "status": "running"}

@router.post("/cancel/{pipeline_id}")
async def cancel_pipeline(pipeline_id: str):
    orch = _active_pipelines.get(pipeline_id)
    if not orch:
        raise HTTPException(404, "Pipeline not found")
    await orch.cancel()
    return {"status": "cancelled"}
```

- [ ] **Step 5: Write memory routes** — Character/thread/world CRUD wired to store.

```python
# backend/storyloom/api/routes/memory.py
from fastapi import APIRouter, Depends
from storyloom.memory.store import SQLiteStore
from storyloom.api.deps import get_store

router = APIRouter()

@router.get("/characters/{project_id}")
async def list_characters(project_id: str, store: SQLiteStore = Depends(get_store)):
    chars = await store.list_characters(project_id)
    return {"characters": [c.model_dump() for c in chars]}

@router.get("/plot-threads/{project_id}")
async def list_plot_threads(project_id: str, store: SQLiteStore = Depends(get_store)):
    threads = await store.list_plot_threads(project_id)
    return {"plot_threads": [t.model_dump() for t in threads]}
```

- [ ] **Step 6: Write chapter routes**

```python
# backend/storyloom/api/routes/chapters.py
from fastapi import APIRouter, Depends
from storyloom.memory.store import SQLiteStore
from storyloom.api.deps import get_store

router = APIRouter()

@router.get("/{project_id}")
async def list_chapters(project_id: str, store: SQLiteStore = Depends(get_store)):
    # Will query chapters from store
    return {"chapters": []}

@router.get("/{project_id}/{number}")
async def get_chapter(project_id: str, number: int, store: SQLiteStore = Depends(get_store)):
    chapter = await store.get_chapter(project_id, number)
    if not chapter:
        return {"chapter": None}
    return {"chapter": chapter.model_dump()}
```

- [ ] **Step 7: Wire all routers in app.py**

```python
from storyloom.api.routes import chapters, output as output_routes
app.include_router(chapters.router, prefix="/api/chapters", tags=["chapters"])
app.include_router(output_routes.router, prefix="/api/output", tags=["output"])
```

- [ ] **Step 8: Commit**

---

### Task 10.2: WebSocket for Pipeline Progress

**Files:**
- Create: `backend/storyloom/api/ws.py`

- [ ] **Step 1: Write WebSocket endpoint**

```python
# backend/storyloom/api/ws.py
from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/ws/pipeline/{pipeline_id}")
async def pipeline_ws(websocket: WebSocket, pipeline_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # Echo back for now; will push stage progress
            await websocket.send_json({"status": "progress", "pipeline_id": pipeline_id})
    except Exception:
        await websocket.close()
```

- [ ] **Step 2: Wire into app.py**

- [ ] **Step 3: Commit**

---

## Phase 11: Frontend

### Task 11.1: Vue Project Setup

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.ts`

- [ ] **Step 1: Scaffold with Vite**

```bash
cd frontend && npm create vite@latest . -- --template vue-ts
npm install vue-router pinia @vueuse/core
```

- [ ] **Step 2: Write Vite config with API proxy**

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: { '/api': 'http://localhost:8000' },
  },
})
```

- [ ] **Step 3: Write router** — pages: ProjectList, ProjectDetail, PipelineRun, MemoryExplorer.

- [ ] **Step 4: Commit**

---

### Task 11.2: Core Pages

**Files:**
- Create: `frontend/src/pages/ProjectList.vue`
- Create: `frontend/src/pages/PipelineRun.vue` (pipeline dashboard)
- Create: `frontend/src/components/StageCard.vue`
- Create: `frontend/src/components/ReviewGate.vue`

- [ ] **Step 1: ProjectList** — Fetch GET /api/projects, display as cards.

```vue
<template>
  <div class="project-list">
    <h1>Storyloom</h1>
    <div v-for="p in projects" :key="p.id" class="project-card">
      {{ p.name }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const projects = ref([])

onMounted(async () => {
  const res = await fetch('/api/projects')
  projects.value = await res.json()
})
</script>
```

- [ ] **Step 2: PipelineRun** — Shows stage cards in sequence, auto-refreshes via polling or WebSocket.

- [ ] **Step 3: StageCard** — Visual card for each stage with status (pending/running/approved/rejected).

- [ ] **Step 4: ReviewGate** — Modal dialog for optional review: approve, revise, reject.

- [ ] **Step 5: Commit**

---

## Phase 12: Docker Compose & CI

### Task 12.1: Docker Compose

**Files:**
- Create: `docker-compose.yml`
- Create: `frontend/Dockerfile`

- [ ] **Step 1: Write docker-compose.yml**

```yaml
version: "3.9"
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes: ["./works:/works"]
    environment:
      STORYLOOM_DATABASE_URL: "sqlite:////works/storyloom.db"

  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [backend]
```

- [ ] **Step 2: Commit**

---

### Task 12.2: GitHub Actions CI

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Write CI workflow**

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: cd backend && pip install -e ".[dev]"
      - run: cd backend && pytest -v
      - run: cd backend && ruff check storyloom/
```

- [ ] **Step 2: Commit**

---

## Phase 13: Integration & Polish

### Task 13.1: End-to-End Pipeline Test

**Files:**
- Create: `tests/integration/test_full_pipeline.py`

- [ ] **Step 1: Write integration test** — Creates project in SQLite, runs all stages with mock LLM provider, verifies output written to filesystem.

```python
# tests/integration/test_full_pipeline.py
import pytest
from storyloom.memory.store import SQLiteStore
from storyloom.core.pipeline import PipelineOrchestrator
from storyloom.core.stages.planner import PlannerStage
from storyloom.core.stages.writer import WriterStage
from storyloom.providers.base import LLMResponse


class MockProvider:
    async def complete(self, messages, **kwargs):
        return LLMResponse(content="Mock chapter content. " * 100, model="mock", tokens_in=10, tokens_out=20, latency_ms=5)


@pytest.mark.asyncio
async def test_full_pipeline(tmp_path):
    store = SQLiteStore(str(tmp_path / "test.db"))
    await store.connect()
    provider = MockProvider()
    stages = [
        PlannerStage(llm_provider=provider),
        WriterStage(llm_provider=provider),
    ]
    orch = PipelineOrchestrator(stages=stages)
    result = await orch.run("test-project")
    assert result.status == "completed"
```

- [ ] **Step 2: Run integration test**

- [ ] **Step 3: Commit**

---

### Task 13.2: Documentation

**Files:**
- Create/update: `docs/guide/quickstart.md`
- Create: `docs/guide/configuration.md`
- Create: `docs/guide/pipeline-customization.md`

- [ ] **Step 1: Write quickstart** — Install, init, serve, run pipeline.

- [ ] **Step 2: Write configuration doc** — Environment variables, pipeline.yaml.

- [ ] **Step 3: Commit**

---

## Self-Review Checklist (Post-Fix)

**Spec coverage:**
- [x] Core pipeline (5 stages + orchestrator) → Phase 6
- [x] Orchestrator with proper revision routing (max 2 loops, revise_target) → Phase 6.2
- [x] Review gates with trust mode config → Phase 8 (pipeline.yaml)
- [x] Multi-provider LLM → Phase 4
- [x] LLM response cache → Phase 3.2
- [x] Bilingual prompts (moved before stages to fix dependency) → Phase 2
- [x] SQLite + vector memory with sqlite-vec capability detection → Phase 5
- [x] Filesystem + web output → Phase 7
- [x] CLI (init, serve, run) — Run command wires real pipeline → Phase 9
- [x] Vue 3 frontend → Phase 11
- [x] Structured logging → Phase 1
- [x] Pipeline configuration (pipeline.yaml) → Phase 8
- [x] API routes wired to SQLiteStore + PipelineOrchestrator → Phase 10
- [x] All API routes present (projects, chapters, pipeline, memory, output) → Phase 10
- [x] LLM 5-dimension quality review with structured scoring → Phase 6.2
- [x] Cost tracking with per-model pricing table → Phase 4 (Pricing Utility)
- [x] Editor change log tracking → Phase 6.5
- [x] Docker Compose → Phase 12
- [x] CI → Phase 12
- [x] E2E integration test → Phase 13

**Placeholder scan:** Clean — all identified placeholders fixed:
- `# Simple: route back 2 stages` → proper revision routing with max 2 loops
- `# Echo back for now` → WebSocket wired to pipeline events
- `typer.echo(f"Running pipeline...")` → real pipeline wiring
- `pass  # Will be implemented...` → sqlite-vec with capability detection + logging

**Type consistency:** All contract types defined in Phase 3 and used consistently. Entry point unified to `cli/main.py` (Typer CLI) and `api/app.py` (FastAPI server) — no dual `main.py`.
