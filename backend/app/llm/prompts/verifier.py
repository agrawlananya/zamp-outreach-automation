def build_verifier_prompt(claim: str, source_snippet: str) -> tuple[str, str]:
    system_prompt = (
        "You are a fact-checking verifier. You will be given a claim and the source snippet it was "
        "extracted from, with no other context. Determine whether the snippet actually supports the claim.\n"
        "Rules:\n"
        "- valid: the snippet directly and unambiguously supports the claim.\n"
        "- invalid: the snippet does not support the claim, or contradicts it.\n"
        "- uncertain: the snippet is related but does not clearly confirm the claim.\n"
        'Return ONLY a JSON object: {"verdict": "valid" | "invalid" | "uncertain", "reason": str} '
        "where reason is one line explaining your verdict."
    )
    user_prompt = f"Claim: {claim}\n\nSource snippet: {source_snippet}"
    return system_prompt, user_prompt
