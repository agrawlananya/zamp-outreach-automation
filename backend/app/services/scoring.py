HOOK_SCORE_SUFFICIENT_THRESHOLD = 0.45


def compute_hook_score(relevance: float, specificity: float, recency: float, actionability: float, verifiability: float) -> float:
    return (
        0.35 * relevance
        + 0.25 * specificity
        + 0.20 * recency
        + 0.10 * actionability
        + 0.10 * verifiability
    )


def score_is_sufficient(hook_score: float) -> bool:
    return hook_score >= HOOK_SCORE_SUFFICIENT_THRESHOLD
