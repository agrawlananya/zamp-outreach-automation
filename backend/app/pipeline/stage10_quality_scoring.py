import json
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.llm.client import call_llm
from app.llm.parsing import parse_json_response
from app.llm.prompts.critic import build_critic_prompt
from app.models.db_models import Draft, Signal


@dataclass
class RubricScore:
    scores: dict
    groundedness_pass: bool


def score_draft(draft: Draft, validated_signals: list[Signal], run_id: str, db: Session) -> RubricScore:
    validated_signal_dicts = [
        {"claim": s.claim, "source_snippet": s.source_snippet, "source_url": s.source_url}
        for s in validated_signals
    ]

    system_prompt, user_prompt = build_critic_prompt(draft.subject, draft.body, validated_signal_dicts)
    response = call_llm(system_prompt, user_prompt)
    parsed = parse_json_response(response)

    scores = parsed.get("scores", {})
    groundedness_pass = bool(parsed.get("groundedness_pass", False))

    draft.rubric_scores = json.dumps(scores)
    draft.groundedness_pass = groundedness_pass
    db.commit()

    return RubricScore(scores=scores, groundedness_pass=groundedness_pass)
