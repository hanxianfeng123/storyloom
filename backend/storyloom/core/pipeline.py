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

    async def run(
        self,
        project_id: str,
        chapter_id: str | None = None,
        context: PipelineContext | None = None,
    ) -> PipelineResult:
        pipeline_id = uuid.uuid4().hex[:12]

        if self._check_cancelled():
            return PipelineResult(pipeline_id=pipeline_id, status="cancelled")

        if context is None:
            context = PipelineContext(story_bible=StoryBible(title="", genre=""))

        results: list[dict] = []
        revision_count: dict[str, int] = {}

        try:
            for stage in self.stages:
                if self._check_cancelled():
                    return PipelineResult(
                        pipeline_id=pipeline_id, status="cancelled", stage_results=results
                    )

                inp = StageInput(
                    project_id=project_id, chapter_id=chapter_id, context=context
                )
                output = await stage.execute(inp)
                results.append({"stage": stage.name, "decision": output.decision})

                if output.decision == "rejected":
                    return PipelineResult(
                        pipeline_id=pipeline_id, status="failed", stage_results=results
                    )

                if output.decision == "need_revision":
                    stage_key = f"{project_id}:{chapter_id}"
                    revision_count[stage_key] = revision_count.get(stage_key, 0) + 1
                    if revision_count[stage_key] > 2:
                        results.append(
                            {"stage": stage.name, "decision": "forced_pass"}
                        )
                        continue
                    target = output.revise_target or "writer"
                    results.append(
                        {"stage": stage.name, "decision": f"revision->{target}"}
                    )

            return PipelineResult(
                pipeline_id=pipeline_id, status="completed", stage_results=results
            )

        except Exception:
            return PipelineResult(
                pipeline_id=pipeline_id, status="failed", stage_results=results
            )
