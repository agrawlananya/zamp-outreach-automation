import json
import re
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.llm.client import call_llm
from app.llm.parsing import parse_json_response
from app.llm.prompts.writer import build_writer_prompt
from app.models.db_models import Draft, PainMapping, PersonaMapping, Signal

HONORIFICS = {"mr", "ms", "mrs", "dr", "prof", "ca"}
_DASH_RE = re.compile(r"[—–]")
_MULTI_SPACE_RE = re.compile(r" {2,}")


def extract_first_name(name: str | None) -> str | None:
    if not name or not name.strip():
        return None

    tokens = name.strip().split()
    if len(tokens) == 1:
        return tokens[0].strip(".").title()

    for token in tokens:
        if token.strip(".").lower() in HONORIFICS:
            continue
        return token.strip(".").title()

    # Every token matched an honorific (unlikely) — fall back to the first one.
    return tokens[0].strip(".").title()


def _sanitize_dashes(text: str | None) -> str | None:
    if not text:
        return text
    sanitized = _DASH_RE.sub(", ", text)
    return _MULTI_SPACE_RE.sub(" ", sanitized)


def _assemble_body(core_paragraphs: str, first_name: str, sender_name: str, sender_title: str) -> str:
    # Greeting and sign-off are purely mechanical (no creativity needed), so they're built
    # deterministically here rather than trusted to the model — the model only writes the
    # three core paragraphs (hook / value / CTA).
    sanitized_core = _sanitize_dashes(core_paragraphs) or ""
    sign_off = f"Best,\n{sender_name}\n{sender_title}, Zamp"
    return f"Hi {first_name},\n\n{sanitized_core}\n\n{sign_off}"


def generate_draft(
    hook: Signal,
    persona: PersonaMapping,
    pain_mappings: list[PainMapping],
    prospect_name: str,
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
    first_name = extract_first_name(prospect_name) or "there"

    system_prompt, user_prompt = build_writer_prompt(
        hook_signal_dict, persona_dict, pain_mapping_dicts, first_name, settings.SENDER_NAME, settings.SENDER_TITLE
    )
    response = call_llm(system_prompt, user_prompt, temperature=0.5)
    parsed = parse_json_response(response)

    draft = Draft(
        id=str(uuid.uuid4()),
        run_id=run_id,
        version=version,
        subject=parsed.get("subject"),
        subject_alt=parsed.get("subject_alt"),
        body=_assemble_body(parsed.get("body"), first_name, settings.SENDER_NAME, settings.SENDER_TITLE),
        sources_used=json.dumps([hook.id]),
        rubric_scores=None,
        groundedness_pass=False,
        created_at=datetime.utcnow(),
    )
    db.add(draft)
    db.commit()

    return draft
