from sqlalchemy.orm import Session

from app.llm.client import call_llm
from app.llm.parsing import parse_json_response
from app.llm.prompts.verifier import build_verifier_prompt
from app.models.db_models import Signal
from app.models.schemas import NormalizedProspect
from app.services.concurrency import run_concurrently

VALID_VALENCES = {"positive", "neutral", "soft_negative", "sensitive"}


def _verify(args: tuple[str, str, str, str, str]) -> tuple[str, str, str, bool]:
    claim, source_snippet, prospect_name, prospect_title, company_name = args
    system_prompt, user_prompt = build_verifier_prompt(
        claim, source_snippet, prospect_name, prospect_title, company_name
    )
    try:
        response = call_llm(system_prompt, user_prompt, max_tokens=256)
        result = parse_json_response(response)
        valence = result.get("valence")
        if valence not in VALID_VALENCES:
            valence = "neutral"
        # Fail closed on entity relevance: only an explicit `true` keeps the signal in play, so a
        # malformed/missing field can't let an off-entity claim slip through.
        about_prospect = result.get("about_prospect") is True
        return result.get("verdict"), result.get("reason"), valence, about_prospect
    except Exception as e:
        # One malformed/failed response shouldn't discard every other signal's validation.
        # Fail closed: an unverifiable signal is treated as not validated, not silently dropped.
        return "invalid", f"Verification call failed: {e}", "neutral", False


def validate_signals(
    signals: list[Signal], prospect: NormalizedProspect, run_id: str, db: Session
) -> list[Signal]:
    validated_signals: list[Signal] = []

    # Read ORM attributes on the main thread first — SQLAlchemy Session objects (and the
    # mapped instances bound to them) aren't safe to touch from worker threads, even for reads.
    verify_args = [
        (s.claim, s.source_snippet, prospect.name, prospect.title, prospect.company_name)
        for s in signals
    ]
    verdicts = run_concurrently(_verify, verify_args, max_workers=4)

    for signal, (verdict, reason, valence, about_prospect) in zip(signals, verdicts):
        snippet_supports = verdict == "valid"
        # "validated" means faithful to its snippet AND actually about this prospect — an
        # off-entity claim (a band/song that merely shares the company's name) is never a usable
        # outreach hook, so it must not reach hook scoring even if the snippet supports it.
        signal.validated = snippet_supports and about_prospect
        if snippet_supports and not about_prospect:
            signal.validation_reason = (
                f"Off-entity: claim about '{signal.entity}', not prospect company "
                f"'{prospect.company_name}'."
            )
        else:
            signal.validation_reason = reason
        signal.valence = valence

        if signal.validated:
            validated_signals.append(signal)

    db.commit()
    return validated_signals
