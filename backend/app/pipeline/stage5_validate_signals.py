from sqlalchemy.orm import Session

from app.llm.client import call_llm
from app.llm.parsing import parse_json_response
from app.llm.prompts.verifier import build_verifier_prompt
from app.models.db_models import Signal


def validate_signals(signals: list[Signal], run_id: str, db: Session) -> list[Signal]:
    validated_signals: list[Signal] = []

    for signal in signals:
        system_prompt, user_prompt = build_verifier_prompt(signal.claim, signal.source_snippet)
        try:
            response = call_llm(system_prompt, user_prompt)
            result = parse_json_response(response)
            verdict = result.get("verdict")
            reason = result.get("reason")
        except Exception as e:
            # One malformed/failed response shouldn't discard every other signal's validation.
            # Fail closed: an unverifiable signal is treated as not validated, not silently dropped.
            verdict = "invalid"
            reason = f"Verification call failed: {e}"

        signal.validated = verdict == "valid"
        signal.validation_reason = reason

        if signal.validated:
            validated_signals.append(signal)

    db.commit()
    return validated_signals
