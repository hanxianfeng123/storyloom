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
            severity="warning",
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

        # Word count check
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
