# Storyloom

AI novel generation platform with multi-LLM pipeline, persistent memory, and bilingual support.

## Quick Start

```bash
pip install storyloom
storyloom init my-novel
storyloom serve
```

## Architecture

Pipeline: Planner -> Writer -> Editor -> Continuity -> Quality Gate -> Output

### Pipeline Stages

- **Planner**: Generates plot outlines, character arcs, and chapter structures from user prompts.
- **Writer**: Produces prose for each chapter following the plan, configurable for different styles and genres.
- **Editor**: Revises output for grammar, pacing, and consistency with the overall narrative.
- **Continuity**: Tracks characters, locations, timelines, and plot threads across chapters to maintain coherence.
- **Quality Gate**: Evaluates output against quality metrics (readability, coherence, style adherence) before finalization.
- **Output**: Formats the final novel into supported output formats (Markdown, EPUB, PDF).

## Features

- **Multi-LLM Pipeline**: Each stage can use a different model provider or configuration.
- **Persistent Memory**: Story state (characters, plot points, world-building) persists across generations.
- **Bilingual Support**: Write and generate in both English and Chinese.
- **Extensible**: Plugin architecture for custom stages, models, and output formats.

## License

MIT
