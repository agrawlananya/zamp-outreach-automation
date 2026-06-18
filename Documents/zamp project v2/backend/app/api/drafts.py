import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.db_models import Draft, ReviewAction, Run
from app.models.schemas import ReviewRequest

router = APIRouter()


@router.patch("/api/drafts/{draft_id}/review")
def review_draft(draft_id: str, payload: ReviewRequest, db: Session = Depends(get_db)):
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")

    review_action = ReviewAction(
        id=str(uuid.uuid4()),
        draft_id=draft_id,
        action=payload.action,
        edited_body=payload.edited_body,
        reason=payload.reason,
        reviewed_at=datetime.utcnow(),
    )
    db.add(review_action)

    run = db.query(Run).filter(Run.id == draft.run_id).first()
    if run is not None:
        run.status = "reviewed"

    db.commit()

    return {"ok": True}
