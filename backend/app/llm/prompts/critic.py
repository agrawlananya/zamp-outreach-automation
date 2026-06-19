import json


def build_critic_prompt(
    subject: str, body: str, validated_signals: list[dict], body_sentences: list[dict]
) -> tuple[str, str]:
    system_prompt = (
        "You are a quality critic for outbound sales emails. Score the draft below against this rubric, "
        "each on a 1-5 scale: relevance, specificity, personalization_depth, credibility, clarity, brevity.\n"
        "Also determine groundedness_pass: true only if BOTH of these hold, else false:\n"
        "1. Every sentence tagged claim_type=\"fact\" in body_sentences maps to one of the supplied "
        "validated signals — no unsupported or invented facts.\n"
        "2. Every sentence tagged claim_type=\"inference\" in body_sentences is clearly hedged (e.g. "
        "\"teams at this stage often find...\", \"this usually means...\") and is NOT phrased as a stated "
        "fact about this specific prospect.\n"
        'Return ONLY a JSON object: {"scores": {"relevance": int, "specificity": int, '
        '"personalization_depth": int, "credibility": int, "clarity": int, "brevity": int}, '
        '"groundedness_pass": bool, "reason": str}.'
    )
    user_prompt = (
        f"Subject: {subject}\n\nBody:\n{body}\n\n"
        f"Body sentences (tagged fact/inference):\n{json.dumps(body_sentences)}\n\n"
        f"Validated signals:\n{json.dumps(validated_signals)}"
    )
    return system_prompt, user_prompt
