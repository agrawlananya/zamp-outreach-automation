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
_ALNUM_RE = re.compile(r"[A-Za-z0-9]")

# EDGE CASE 2 (valence gate): banned tokens for soft_negative hooks — celebratory language
# is tone-deaf when the hook is cost pressure, a hiring freeze, or missed targets.
SOFT_NEGATIVE_BANNED_TOKENS = [
    "congrats",
    "congratulations",
    "exciting",
    "excited",
    "momentum",
    "thrilled",
    "big news",
]

VALID_SENTENCE_TYPES = {"fact", "inference"}


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


def _clean_subject(value: str | None) -> str | None:
    # Guards against degenerate LLM output (empty, whitespace, or punctuation-only subjects).
    if not value:
        return None
    value = value.strip()
    return value if _ALNUM_RE.search(value) else None


def _normalize_body_sentences(raw_sentences: list[dict] | None, hook_id: str) -> list[dict]:
    # EDGE CASE 4: the model tags fact vs inference, but signal_id is attached here in code
    # rather than trusted from the model — the only factual source in context is the hook itself.
    normalized = []
    for entry in raw_sentences or []:
        text = _sanitize_dashes(entry.get("text")) or ""
        if not text:
            continue
        sentence_type = entry.get("type") if entry.get("type") in VALID_SENTENCE_TYPES else "fact"
        normalized.append({
            "paragraph": entry.get("paragraph") or 1,
            "text": text,
            "type": sentence_type,
            "signal_id": hook_id if sentence_type == "fact" else None,
        })
    return normalized


def _core_body_from_sentences(body_sentences: list[dict]) -> str:
    paragraphs: dict[int, list[str]] = {}
    for entry in body_sentences:
        paragraphs.setdefault(entry["paragraph"], []).append(entry["text"])
    return "\n\n".join(" ".join(paragraphs[p]) for p in sorted(paragraphs))


def _assemble_body(core_paragraphs: str, first_name: str, sender_name: str, sender_title: str) -> str:
    # Greeting and sign-off are purely mechanical (no creativity needed), so they're built
    # deterministically here rather than trusted to the model — the model only writes the
    # three core paragraphs (hook / value / CTA).
    sign_off = f"Best,\n{sender_name}\n{sender_title}, Zamp"
    return f"Hi {first_name},\n\n{core_paragraphs}\n\n{sign_off}"


def generate_draft(
    hook: Signal,
    persona: PersonaMapping,
    pain_mappings: list[PainMapping],
    prospect_name: str,
    run_id: str,
    db: Session,
    version: int = 1,
    new_in_role: bool = False,
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

    # EDGE CASE 2: soft_negative hooks get a banned-token + tone instruction in the prompt.
    banned_tokens = SOFT_NEGATIVE_BANNED_TOKENS if hook.valence == "soft_negative" else None

    system_prompt, user_prompt = build_writer_prompt(
        hook_signal_dict, persona_dict, pain_mapping_dicts, first_name, settings.SENDER_NAME, settings.SENDER_TITLE,
        new_in_role=new_in_role, banned_tokens=banned_tokens,
    )
    response = call_llm(system_prompt, user_prompt, temperature=0.5)
    parsed = parse_json_response(response)

    body_sentences = _normalize_body_sentences(parsed.get("body_sentences"), hook.id)
    core_body = _core_body_from_sentences(body_sentences)

    default_subject = f"quick note for {first_name}"
    subject = _clean_subject(parsed.get("subject")) or _clean_subject(parsed.get("subject_alt")) or default_subject
    subject_alt = _clean_subject(parsed.get("subject_alt")) or _clean_subject(parsed.get("subject")) or default_subject

    draft = Draft(
        id=str(uuid.uuid4()),
        run_id=run_id,
        version=version,
        subject=subject,
        subject_alt=subject_alt,
        body=_assemble_body(core_body, first_name, settings.SENDER_NAME, settings.SENDER_TITLE),
        derived_consequence=_sanitize_dashes(parsed.get("derived_consequence")),
        body_sentences=json.dumps(body_sentences),
        sources_used=json.dumps([hook.id]),
        rubric_scores=None,
        groundedness_pass=False,
        created_at=datetime.utcnow(),
    )
    db.add(draft)
    db.commit()

    return draft
