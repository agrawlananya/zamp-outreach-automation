import json
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models.db_models import Draft, Run, Signal


def personalization_depth(run: Run, db: Session) -> int:
    top_signal = (
        db.query(Signal).filter(Signal.run_id == run.id, Signal.selected_as_hook == True).first()  # noqa: E712
    )
    if top_signal is None:
        return 0
    return 2 if top_signal.scope == "individual" else 1


def groundedness_ratio(draft: Draft | None) -> tuple[int, int, int]:
    if draft is None:
        return 0, 0, 0

    if not draft.body_sentences:
        return (1, 1, 100) if draft.groundedness_pass else (0, 1, 0)

    sentences = json.loads(draft.body_sentences)
    facts = [s for s in sentences if s.get("type") == "fact"]
    total = len(facts)
    grounded = sum(1 for s in facts if s.get("signal_id"))
    pct = round(100 * grounded / total) if total else 0
    return grounded, total, pct


def hook_signal_type_and_domain(run_id: str, db: Session) -> tuple[str | None, str | None]:
    top_signal = (
        db.query(Signal).filter(Signal.run_id == run_id, Signal.selected_as_hook == True).first()  # noqa: E712
    )
    if top_signal is None:
        return None, None
    domain = urlparse(top_signal.source_url).netloc if top_signal.source_url else None
    return top_signal.type, domain
