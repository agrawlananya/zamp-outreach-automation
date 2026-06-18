from sqlalchemy.orm import Session

from app.models.db_models import Prospect
from app.models.schemas import NormalizedProspect


def intake_and_normalize(prospect_id: str, db: Session) -> NormalizedProspect:
    prospect = db.query(Prospect).filter(Prospect.id == prospect_id).one()

    # V1 heuristic: lowercase company name, strip spaces, add .com — good enough for MVP.
    company_domain = prospect.company_name.lower().replace(" ", "") + ".com"

    prospect.company_domain = company_domain
    db.commit()

    return NormalizedProspect(
        id=prospect.id,
        name=prospect.name,
        title=prospect.title,
        company_name=prospect.company_name,
        company_domain=company_domain,
    )
