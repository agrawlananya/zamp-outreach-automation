from sqlalchemy.orm import Session

from app.llm.client import call_llm
from app.llm.parsing import parse_json_response
from app.llm.prompts.verifier import build_verifier_prompt
from app.models.db_models import Signal
from app.services.concurrency import run_concurrently


def _verify(claim_and_snippet: tuple[str, str]) -> tuple[str, str]:
    claim, source_snippet = claim_and_snippet
    system_prompt, user_prompt = build_verifier_prompt(claim, source_snippet)
    try:
        response = call_llm(system_prompt, user_prompt)
        result = parse_json_response(response)
        return result.get("verdict"), result.get("reason")
    except Exception as e:
        # One malformed/failed response shouldn't discard every other signal's validation.
        # Fail closed: an unverifiable signal is treated as not validated, not silently dropped.
        return "invalid", f"Verification call failed: {e}"


def validate_signals(signals: list[Signal], run_id: str, db: Session) -> list[Signal]:
    validated_signals: list[Signal] = []

    # Read ORM attributes on the main thread first — SQLAlchemy Session objects (and the
    # mapped instances bound to them) aren't safe to touch from worker threads, even for reads.
    claims_and_snippets = [(s.claim, s.source_snippet) for s in signals]
    verdicts = run_concurrently(_verify, claims_and_snippets, max_workers=4)

    for signal, (verdict, reason) in zip(signals, verdicts):
        signal.validated = verdict == "valid"
        signal.validation_reason = reason

        if signal.validated:
            validated_signals.append(signal)

    db.commit()
    return validated_signals
