import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.llm.client import call_llm
from app.llm.parsing import parse_json_response
from app.llm.prompts.extractor import build_extractor_prompt
from app.models.db_models import Signal
from app.models.schemas import RawCorpus


def _parse_signal_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def extract_signals(corpora: list[RawCorpus], run_id: str, db: Session) -> list[Signal]:
    signals: list[Signal] = []

    for corpus in corpora:
        for item in corpus.items:
            if not item.body_text:
                continue

            system_prompt, user_prompt = build_extractor_prompt(item.body_text, item.url)
            try:
                response = call_llm(system_prompt, user_prompt)
                extracted = parse_json_response(response)
            except Exception:
                # One malformed/failed extraction shouldn't discard signals already
                # extracted from other corpus items.
                continue

            for entry in extracted:
                signal = Signal(
                    id=str(uuid.uuid4()),
                    run_id=run_id,
                    scope=entry.get("scope"),
                    type=entry.get("type"),
                    claim=entry.get("claim"),
                    source_url=item.url,
                    source_snippet=entry.get("source_snippet"),
                    signal_date=_parse_signal_date(entry.get("signal_date")),
                    entity=entry.get("entity"),
                    validated=False,
                )
                db.add(signal)
                signals.append(signal)

    db.commit()
    return signals
