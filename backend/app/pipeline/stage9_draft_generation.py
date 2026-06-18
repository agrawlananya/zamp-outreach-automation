import json
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.llm.client import call_llm
from app.llm.parsing import parse_json_response
from app.llm.prompts.writer import build_writer_prompt
from app.models.db_models import Draft, PainMapping, PersonaMapping, Signal


def generate_draft(
    hook: Signal,
    persona: PersonaMapping,
    pain_mappings: list[PainMapping],
    run_id: str,
    db: Session,
    version: int = 1,
) -> Draft:
    hook_signal_dict = {
        "type": hook.type,
        "claim": hook.claim,
        "source_url": hook.source_url,
        "source_snippet": hook.source_snippet,
        "entity": hook.entity,
        "signal_date": str(hook.signal_date) if hook.signal_date else None,
    }
    persona_dict = {
        "name": persona.persona_name,
        "goals": json.loads(persona.goals),
        "pains": json.loads(persona.pains),
        "kpis": json.loads(persona.kpis),
    }
    pain_mapping_dicts = [
        {"owned_pain": pm.owned_pain, "owned_kpi": pm.owned_kpi, "zamp_value_prop": pm.zamp_value_prop}
        for pm in pain_mappings
    ]

    system_prompt, user_prompt = build_writer_prompt(hook_signal_dict, persona_dict, pain_mapping_dicts)
    response = call_llm(system_prompt, user_prompt, temperature=0.5)
    parsed = parse_json_response(response)

    draft = Draft(
        id=str(uuid.uuid4()),
        run_id=run_id,
        version=version,
        subject=parsed.get("subject"),
        body=parsed.get("body"),
        sources_used=json.dumps([hook.id]),
        rubric_scores=None,
        groundedness_pass=False,
        created_at=datetime.utcnow(),
    )
    db.add(draft)
    db.commit()

    return draft
