import asyncio
import uuid
from dataclasses import dataclass, field

from storyloom.core.stages.base import Stage
from storyloom.core.contract import StageInput, PipelineContext, StoryBible, SupervisorResult
from storyloom.core.skills.supervisor import SupervisorPipeline

MAX_REVISIONS = 2


@dataclass
class PipelineResult:
    pipeline_id: str
    status: str  # completed | failed | cancelled
    stage_results: list[dict] = field(default_factory=list)


class PipelineOrchestrator:
    def __init__(
        self,
        stages: list[Stage] | None = None,
        supervisor_pipeline: SupervisorPipeline | None = None,
    ):
        self.stages = stages or []
        self._supervisor_pipeline = supervisor_pipeline
        self._cancel_event = asyncio.Event()

    async def cancel(self):
        self._cancel_event.set()

    def _check_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    async def run(
        self,
        project_id: str,
        chapter_id: str | None = None,
        context: PipelineContext | None = None,
        use_supervisor: bool = False,
    ) -> PipelineResult | SupervisorResult:
        pipeline_id = uuid.uuid4().hex[:12]

        if self._check_cancelled():
            return PipelineResult(pipeline_id=pipeline_id, status="cancelled")

        if context is None:
            context = PipelineContext(story_bible=StoryBible(title="", genre=""))

        context.project_id = project_id

        if use_supervisor and self._supervisor_pipeline:
            return await self._supervisor_pipeline.run(context, pipeline_id)

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
                    stage_key = f"{stage.name}:{project_id}:{chapter_id}"
                    revision_count[stage_key] = revision_count.get(stage_key, 0) + 1

                    if revision_count[stage_key] > MAX_REVISIONS:
                        results.append({"stage": stage.name, "decision": "forced_pass"})
                        continue

                    # Re-run the target stage until approved or max retries
                    target_name = output.revise_target or "writer"
                    target_stage = next(
                        (s for s in self.stages if s.name == target_name), None
                    )
                    if not target_stage:
                        continue

                    revision_hint = output.revision_context
                    for attempt in range(MAX_REVISIONS):
                        if revision_hint:
                            inp.context.revision_hint = revision_hint
                        retry_output = await target_stage.execute(inp)
                        results.append({
                            "stage": f"{target_name}(revision#{attempt + 1})",
                            "decision": retry_output.decision,
                        })

                        if retry_output.decision in ("approved",):
                            break
                        if retry_output.decision == "rejected":
                            return PipelineResult(
                                pipeline_id=pipeline_id,
                                status="failed",
                                stage_results=results,
                            )
                        if attempt < MAX_REVISIONS - 1:
                            revision_context = getattr(retry_output, "revision_context", None)
                            if revision_context:
                                revision_hint = revision_context
                    else:
                        results.append({"stage": target_name, "decision": "forced_pass"})

            return PipelineResult(
                pipeline_id=pipeline_id, status="completed", stage_results=results
            )

        except Exception:
            return PipelineResult(
                pipeline_id=pipeline_id, status="failed", stage_results=results
            )
