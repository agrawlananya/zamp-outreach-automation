from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.db_models import Draft, ReviewAction, Run
from app.models.schemas import MetricsResponse
from app.services.run_readmodel import personalization_depth

router = APIRouter()

NON_TERMINAL_STATUSES = ("pending", "running")
ESCALATION_STATUSES = ("insufficient_signal", "needs_human_research")


@router.get("/api/metrics", response_model=MetricsResponse)
def get_metrics(db: Session = Depends(get_db)):
    review_actions = db.query(ReviewAction).all()
    total_reviewed = len(review_actions)
    accepted = sum(1 for r in review_actions if r.action != "reject")
    acceptance_rate = accepted / total_reviewed if total_reviewed else 0.0

    drafts = db.query(Draft).all()
    groundedness_drafts_pass = sum(1 for d in drafts if d.groundedness_pass)
    groundedness_drafts_total = len(drafts)
    groundedness_pct = groundedness_drafts_pass / groundedness_drafts_total if groundedness_drafts_total else 0.0

    all_runs = db.query(Run).all()
    completed_runs = [r for r in all_runs if r.status not in NON_TERMINAL_STATUSES]
    escalated_runs = [r for r in completed_runs if r.status in ESCALATION_STATUSES]
    escalation_rate = len(escalated_runs) / len(completed_runs) if completed_runs else 0.0

    times = [r.time_to_draft_ms for r in all_runs if r.time_to_draft_ms is not None]
    avg_time_to_draft_ms = sum(times) / len(times) if times else 0.0

    depths = [personalization_depth(run, db) for run in all_runs]
    avg_personalization_depth = sum(depths) / len(depths) if depths else 0.0

    return MetricsResponse(
        acceptance_rate=acceptance_rate,
        groundedness_pct=groundedness_pct,
        escalation_rate=escalation_rate,
        avg_time_to_draft_ms=avg_time_to_draft_ms,
        avg_personalization_depth=avg_personalization_depth,
        accepted_count=accepted,
        reviewed_count=total_reviewed,
        groundedness_drafts_pass=groundedness_drafts_pass,
        groundedness_drafts_total=groundedness_drafts_total,
        escalated_count=len(escalated_runs),
        completed_count=len(completed_runs),
    )
