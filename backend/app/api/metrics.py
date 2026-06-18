from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.db_models import Draft, ReviewAction, Run, Signal
from app.models.schemas import MetricsResponse

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
    groundedness_pct = sum(1 for d in drafts if d.groundedness_pass) / len(drafts) if drafts else 0.0

    all_runs = db.query(Run).all()
    completed_runs = [r for r in all_runs if r.status not in NON_TERMINAL_STATUSES]
    escalated_runs = [r for r in completed_runs if r.status in ESCALATION_STATUSES]
    escalation_rate = len(escalated_runs) / len(completed_runs) if completed_runs else 0.0

    times = [r.time_to_draft_ms for r in all_runs if r.time_to_draft_ms is not None]
    avg_time_to_draft_ms = sum(times) / len(times) if times else 0.0

    depths = []
    for run in all_runs:
        top_signal = (
            db.query(Signal).filter(Signal.run_id == run.id, Signal.selected_as_hook == True).first()  # noqa: E712
        )
        if top_signal is None:
            depths.append(0)
        elif top_signal.scope == "individual":
            depths.append(2)
        else:
            depths.append(1)
    avg_personalization_depth = sum(depths) / len(depths) if depths else 0.0

    return MetricsResponse(
        acceptance_rate=acceptance_rate,
        groundedness_pct=groundedness_pct,
        escalation_rate=escalation_rate,
        avg_time_to_draft_ms=avg_time_to_draft_ms,
        avg_personalization_depth=avg_personalization_depth,
    )
