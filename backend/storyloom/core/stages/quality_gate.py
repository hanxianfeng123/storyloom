# DEPRECATED — will be removed in favor of DB-driven skills (definitions.yaml → quality).
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

    def __init__(self, model: str = "anthropic/claude-sonnet-4-20250514"):
        self._model = model

    async def _llm_review(self, chapter_text: str, language: str = "zh") -> dict:
        """Run 5-dimension LLM review on a chapter."""
        from storyloom.i18n.zh.prompts.quality import QUALITY_SYSTEM_PROMPT
        from storyloom.i18n.en.prompts.quality import QUALITY_SYSTEM_PROMPT as EN_QUALITY_SYSTEM_PROMPT
        from storyloom.providers.litellm import complete
        import json

        prompt = QUALITY_SYSTEM_PROMPT if language == "zh" else EN_QUALITY_SYSTEM_PROMPT

        messages = [
            {"role": "system", "content": prompt + "\n\nRespond ONLY with a JSON object."},
            {"role": "user", "content": f"Chapter:\n{chapter_text[:4000]}\n\nRate each dimension pass/flag/fail with reason."},
        ]
        response = await complete(messages, model=self._model, max_tokens=1024)
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

    async def execute(self, input: StageInput) -> StageOutput:
        ctx = input.context
        issues: list[QualityIssue] = []

        # Word count check
        if ctx.chapter_history:
            last_ch = ctx.chapter_history[-1]
            issues.extend(check_word_count(target=2000, actual=last_ch.word_count))

        # LLM 5-dimension review
        if input.chapter_id:
            language = "zh"  # Could be made configurable
            llm_scores = await self._llm_review(str(input.chapter_id)[:4000], language)
            llm_fails = [k for k, v in llm_scores.items() if isinstance(v, dict) and v.get("score") == "fail"]
            if llm_fails:
                issues.append(QualityIssue(
                    check="llm_review",
                    severity="critical",
                    message=f"Failed dimensions: {', '.join(llm_fails)}",
                ))

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
