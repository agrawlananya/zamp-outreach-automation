import json
import uuid

from sqlalchemy.orm import Session

from app.models.db_models import PersonaMapping
from app.services.persona_library import lookup_persona


def map_persona(title: str, run_id: str, db: Session) -> PersonaMapping:
    persona, is_assumed = lookup_persona(title)

    persona_mapping = PersonaMapping(
        id=str(uuid.uuid4()),
        run_id=run_id,
        persona_name=persona["name"],
        is_assumed=is_assumed,
        goals=json.dumps(persona["goals"]),
        pains=json.dumps(persona["pains"]),
        kpis=json.dumps(persona["kpis"]),
    )
    db.add(persona_mapping)
    db.commit()

    return persona_mapping
