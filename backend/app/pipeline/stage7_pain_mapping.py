import json
import uuid

from sqlalchemy.orm import Session

from app.llm.client import call_llm
from app.llm.parsing import parse_json_response
from app.models.db_models import PainMapping, PersonaMapping, Signal


def _build_pain_prompt(claim: str, pains: list[str]) -> tuple[str, str]:
    system_prompt = (
        "Given a sales signal claim and a fixed list of persona pains, pick the single pain the claim "
        "most relates to, and propose the KPI it affects and a one-line Zamp value proposition tied to it. "
        'Return ONLY a JSON object: {"owned_pain": str, "owned_kpi": str, "zamp_value_prop": str}. '
        "owned_pain must be exactly one of the supplied pains."
    )
    user_prompt = f"Claim: {claim}\n\nPersona pains: {json.dumps(pains)}"
    return system_prompt, user_prompt


def map_pain(signals: list[Signal], persona: PersonaMapping, run_id: str, db: Session) -> list[PainMapping]:
    pains = json.loads(persona.pains)
    pain_mappings: list[PainMapping] = []

    for signal in signals:
        system_prompt, user_prompt = _build_pain_prompt(signal.claim, pains)
        try:
            response = call_llm(system_prompt, user_prompt)
            result = parse_json_response(response)
        except Exception:
            # One malformed/failed pain-mapping call shouldn't discard every other signal's mapping.
            continue

        pain_mapping = PainMapping(
            id=str(uuid.uuid4()),
            run_id=run_id,
            signal_id=signal.id,
            owned_pain=result.get("owned_pain"),
            owned_kpi=result.get("owned_kpi"),
            zamp_value_prop=result.get("zamp_value_prop"),
        )
        db.add(pain_mapping)
        pain_mappings.append(pain_mapping)

    db.commit()
    return pain_mappings
