import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.db_models import AuditLog, Draft, PainMapping, PersonaMapping, Prospect, ReviewAction, Run, Signal
from app.models.schemas import (
    AuditLogOut,
    DraftOut,
    PainMappingOut,
    PersonaMappingOut,
    RunDetailResponse,
    RunStatusResponse,
    SignalOut,
)
from app.pipeline.orchestrator import run_pipeline_in_background

router = APIRouter()

STAGE_ORDER = [
    "stage1_intake",
    "stage2_research",
    "stage4_extract_signals",
    "stage5_validate_signals",
    "stage6_persona_mapping",
    "stage7_pain_mapping",
    "stage8_hook_scoring",
    "stage9_draft_generation",
    "stage10_quality_scoring",
    "stage11_routing",
]
STAGE_PERCENT = {name: round((i + 1) / len(STAGE_ORDER) * 100) for i, name in enumerate(STAGE_ORDER)}
NON_TERMINAL_STATUSES = ("pending", "running")


@router.get("/api/runs/{run_id}", response_model=RunDetailResponse)
def get_run_detail(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    signals = db.query(Signal).filter(Signal.run_id == run_id).all()
    persona_mapping = db.query(PersonaMapping).filter(PersonaMapping.run_id == run_id).first()
    pain_mappings = db.query(PainMapping).filter(PainMapping.run_id == run_id).all()
    latest_draft = db.query(Draft).filter(Draft.run_id == run_id).order_by(Draft.version.desc()).first()
    audit_log = db.query(AuditLog).filter(AuditLog.run_id == run_id).order_by(AuditLog.created_at).all()

    return RunDetailResponse(
        id=run.id,
        prospect_id=run.prospect_id,
        status=run.status,
        current_stage=run.current_stage,
        started_at=run.started_at,
        completed_at=run.completed_at,
        time_to_draft_ms=run.time_to_draft_ms,
        escalation_reason=run.escalation_reason,
        signals=[SignalOut.model_validate(s) for s in signals],
        persona_mapping=PersonaMappingOut.model_validate(persona_mapping) if persona_mapping else None,
        pain_mappings=[PainMappingOut.model_validate(pm) for pm in pain_mappings],
        draft=DraftOut.model_validate(latest_draft) if latest_draft else None,
        audit_log=[AuditLogOut.model_validate(a) for a in audit_log],
    )


@router.get("/api/runs/{run_id}/status", response_model=RunStatusResponse)
def get_run_status(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    if run.status in NON_TERMINAL_STATUSES:
        percent_complete = STAGE_PERCENT.get(run.current_stage, 0)
    else:
        percent_complete = 100

    return RunStatusResponse(status=run.status, current_stage=run.current_stage, percent_complete=percent_complete)


@router.get("/api/runs")
def list_runs(
    status: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Run)
    if status:
        query = query.filter(Run.status == status)

    total = query.count()
    runs = query.order_by(Run.started_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    items = []
    for run in runs:
        prospect = db.query(Prospect).filter(Prospect.id == run.prospect_id).first()
        top_signal = (
            db.query(Signal).filter(Signal.run_id == run.id, Signal.selected_as_hook == True).first()  # noqa: E712
        )
        latest_draft = db.query(Draft).filter(Draft.run_id == run.id).order_by(Draft.version.desc()).first()
        review_action = (
            db.query(ReviewAction)
            .filter(ReviewAction.draft_id == latest_draft.id)
            .order_by(ReviewAction.reviewed_at.desc())
            .first()
            if latest_draft
            else None
        )
        items.append(
            {
                "id": run.id,
                "prospect_name": prospect.name if prospect else None,
                "company": prospect.company_name if prospect else None,
                "status": run.status,
                "top_hook_score": top_signal.hook_score if top_signal else None,
                "time_to_draft_ms": run.time_to_draft_ms,
                "human_decision": review_action.action if review_action else None,
                "created_at": run.started_at,  # runs has no created_at column; started_at is the closest analog
            }
        )

    return {"items": items, "page": page, "per_page": per_page, "total": total}


@router.post("/api/runs/{run_id}/retry")
def retry_run(run_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.status != "failed":
        raise HTTPException(status_code=400, detail="Only failed runs can be retried")

    new_run = Run(id=str(uuid.uuid4()), prospect_id=run.prospect_id, status="pending", started_at=datetime.utcnow())
    db.add(new_run)
    db.commit()

    background_tasks.add_task(run_pipeline_in_background, new_run.id)

    return {"new_run_id": new_run.id}
