from app.pipeline.stage8_hook_scoring import HookSelection
from app.pipeline.stage10_quality_scoring import RubricScore


def route(hook_selection: HookSelection, rubric_score: RubricScore) -> str:
    if not hook_selection.top_score_sufficient:
        return "insufficient_signal"
    if not rubric_score.groundedness_pass:
        return "needs_human_research"
    return "ready_for_review"
