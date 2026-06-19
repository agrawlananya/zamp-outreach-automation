from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.db_models import PainMapping, Signal
from app.services.scoring import compute_hook_score, score_is_sufficient

ACTIONABLE_TYPES = {
    "role_change",
    "leadership_change",
    "funding_round",
    "acquisition",
    "ipo_prep",
    "merger",
    "reorg",
    "regulatory_change",
    "system_migration",
}

# EDGE CASE 3 (saturation penalty): categories that are "template-bait" — widely syndicated,
# easy for any competitor to find and use the same way.
TEMPLATE_BAIT_TYPES = {
    "funding_round",
    "executive_hire",
    "award",
    "product_launch",
    "partnership",
    "acquisition",
    "ipo_prep",
}


@dataclass
class HookSubScores:
    relevance: float
    specificity: float
    recency: float
    actionability: float
    verifiability: float


@dataclass
class HookCandidate:
    signal_id: str
    hook_score: float
    adjusted_hook_score: float
    sub_scores: HookSubScores


@dataclass
class HookSelection:
    selected_signal: Signal | None
    all_scores: list[HookCandidate]
    top_score_sufficient: bool


def _score_relevance(signal: Signal, pain_mapped_signal_ids: set[str]) -> float:
    return 1.0 if signal.id in pain_mapped_signal_ids else 0.3


def _score_specificity(signal: Signal) -> float:
    has_entity = bool(signal.entity)
    has_specific_claim = bool(signal.claim) and len(signal.claim) > 20
    return 1.0 if has_entity and has_specific_claim else 0.5


def _score_recency(signal: Signal) -> float:
    if not signal.signal_date:
        return 0.1
    signal_date = signal.signal_date
    if isinstance(signal_date, datetime):
        signal_date = signal_date.date()
    age_days = (date.today() - signal_date).days
    if age_days <= 90:
        return 1.0
    if age_days <= 180:
        return 0.7
    if age_days <= 365:
        return 0.3
    return 0.1


def _score_actionability(signal: Signal) -> float:
    signal_type = signal.type or ""
    is_actionable = (
        signal_type.startswith("new_")
        or signal_type.endswith("_migration")
        or signal_type in ACTIONABLE_TYPES
    )
    return 1.0 if is_actionable else 0.5


def _score_verifiability(signal: Signal) -> float:
    return 1.0 if signal.source_snippet and len(signal.source_snippet) > 50 else 0.5


def _score_saturation(signal: Signal, all_signals: list[Signal]) -> float:
    """EDGE CASE 3: heuristic 0-1 estimate of how widely covered/obvious a signal is, computed
    entirely from data already fetched for this run (no new search calls). Inputs: whether the
    type is a "template-bait" category, how many OTHER distinct sources in this same run cover
    the same entity+type (a cheap proxy for syndication), and how stale the news cycle is."""
    is_template_bait = (signal.type or "") in TEMPLATE_BAIT_TYPES

    distinct_sources = {
        other.source_url
        for other in all_signals
        if signal.entity and other.entity == signal.entity and other.type == signal.type and other.source_url
    }
    duplicate_count = max(len(distinct_sources) - 1, 0)

    recency = _score_recency(signal)

    saturation = (
        0.4 * (1.0 if is_template_bait else 0.0)
        + 0.4 * min(duplicate_count / 3, 1.0)
        + 0.2 * (1.0 - recency)
    )
    return min(1.0, max(0.0, saturation))


def rank_candidate_signals(signals: list[Signal], limit: int = 8) -> list[Signal]:
    """Cheaply pre-rank validated signals on the four sub-scores that don't require
    pain-mapping (relevance is excluded — it can only be computed after pain-mapping
    has run), so expensive per-signal LLM work downstream only happens for the
    signals with a real shot at being selected as the hook."""
    def candidate_score(signal: Signal) -> float:
        return (
            _score_specificity(signal)
            + _score_recency(signal)
            + _score_actionability(signal)
            + _score_verifiability(signal)
        )

    return sorted(signals, key=candidate_score, reverse=True)[:limit]


def score_and_select_hook(
    signals: list[Signal],
    pain_mappings: list[PainMapping],
    run_id: str,
    db: Session,
    force_low_confidence: bool = False,
) -> HookSelection:
    pain_mapped_signal_ids = {pm.signal_id for pm in pain_mappings}

    candidates: list[HookCandidate] = []
    best_signal: Signal | None = None
    best_adjusted_score = -1.0

    for signal in signals:
        sub_scores = HookSubScores(
            relevance=_score_relevance(signal, pain_mapped_signal_ids),
            specificity=_score_specificity(signal),
            recency=_score_recency(signal),
            actionability=_score_actionability(signal),
            verifiability=_score_verifiability(signal),
        )

        if force_low_confidence:
            # EC-1: no public data on either side — cap every sub-score so hook_score
            # naturally falls below the insufficient_signal threshold.
            sub_scores = HookSubScores(
                relevance=min(sub_scores.relevance, 0.1),
                specificity=min(sub_scores.specificity, 0.1),
                recency=min(sub_scores.recency, 0.1),
                actionability=min(sub_scores.actionability, 0.1),
                verifiability=min(sub_scores.verifiability, 0.1),
            )

        hook_score = compute_hook_score(
            sub_scores.relevance,
            sub_scores.specificity,
            sub_scores.recency,
            sub_scores.actionability,
            sub_scores.verifiability,
        )

        # EDGE CASE 2 (valence gate): sensitive signals are factually still true (sub-scores
        # are left as computed, for trail transparency) but are never eligible as an outreach hook.
        if signal.valence == "sensitive":
            hook_score = 0.0

        saturation = _score_saturation(signal, signals)
        # EDGE CASE 3 (saturation penalty): the signal stays true; only its outreach value is
        # discounted. The raw hook_score is kept as-is for the trail, selection uses adjusted.
        adjusted_hook_score = hook_score * (1 - 0.5 * saturation)

        signal.relevance_score = sub_scores.relevance
        signal.specificity_score = sub_scores.specificity
        signal.recency_score = sub_scores.recency
        signal.actionability_score = sub_scores.actionability
        signal.verifiability_score = sub_scores.verifiability
        signal.hook_score = hook_score
        signal.saturation = saturation
        signal.adjusted_hook_score = adjusted_hook_score
        signal.selected_as_hook = False

        candidates.append(
            HookCandidate(
                signal_id=signal.id,
                hook_score=hook_score,
                adjusted_hook_score=adjusted_hook_score,
                sub_scores=sub_scores,
            )
        )

        if adjusted_hook_score > best_adjusted_score:
            best_adjusted_score = adjusted_hook_score
            best_signal = signal

    if best_signal is not None:
        best_signal.selected_as_hook = True

    db.commit()

    return HookSelection(
        selected_signal=best_signal,
        all_scores=candidates,
        top_score_sufficient=score_is_sufficient(best_adjusted_score) if best_signal is not None else False,
    )
