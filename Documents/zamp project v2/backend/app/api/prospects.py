import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.db_models import Prospect, Run
from app.models.schemas import ProspectCreate
from app.pipeline.orchestrator import run_pipeline_in_background

router = APIRouter()


@router.post("/api/prospects")
def create_prospect(payload: ProspectCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    prospect = Prospect(
        id=str(uuid.uuid4()),
        name=payload.name,
        title=payload.title,
        company_name=payload.company_name,
        created_at=datetime.utcnow(),
    )
    db.add(prospect)
    db.commit()

    run = Run(id=str(uuid.uuid4()), prospect_id=prospect.id, status="pending", started_at=datetime.utcnow())
    db.add(run)
    db.commit()

    background_tasks.add_task(run_pipeline_in_background, run.id)

    return {"run_id": run.id}
