import json


def build_critic_prompt(subject: str, body: str, validated_signals: list[dict]) -> tuple[str, str]:
    system_prompt = (
        "You are a quality critic for outbound sales emails. Score the draft below against this rubric, "
        "each on a 1-5 scale: relevance, specificity, personalization_depth, credibility, clarity, brevity.\n"
        "Also determine groundedness_pass: true only if EVERY factual claim in the email body maps to one "
        "of the supplied validated signals; false if any claim is unsupported or invented.\n"
        'Return ONLY a JSON object: {"scores": {"relevance": int, "specificity": int, '
        '"personalization_depth": int, "credibility": int, "clarity": int, "brevity": int}, '
        '"groundedness_pass": bool, "reason": str}.'
    )
    user_prompt = (
        f"Subject: {subject}\n\nBody:\n{body}\n\nValidated signals:\n{json.dumps(validated_signals)}"
    )
    return system_prompt, user_prompt
