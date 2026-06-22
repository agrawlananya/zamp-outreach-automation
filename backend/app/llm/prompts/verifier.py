def build_verifier_prompt(
    claim: str,
    source_snippet: str,
    prospect_name: str,
    prospect_title: str,
    company_name: str,
) -> tuple[str, str]:
    system_prompt = (
        "You are a fact-checking verifier. Given a claim, the snippet it was extracted "
        "from, and the sales prospect, judge three things:\n"
        "VERDICT (from the SNIPPET ALONE — ignore prospect context here):\n"
        "- valid: snippet directly and unambiguously supports the claim.\n"
        "- invalid: snippet does not support the claim, or contradicts it.\n"
        "- uncertain: snippet is related but does not clearly confirm the claim.\n"
        "VALENCE (classify the claim itself, regardless of verdict):\n"
        "- sensitive: layoffs framed negatively, scandal, investigation, lawsuit, data "
        "breach, an individual ousted/fired, death/tragedy, bankruptcy.\n"
        "- soft_negative: cost pressure, hiring freeze, missed targets, \"do more with "
        "less\" — negative but not sensitive.\n"
        "- positive: good news, growth, wins, recognition.\n"
        "- neutral: factual/operational, no clear charge.\n"
        "ABOUT_PROSPECT (use the prospect context):\n"
        "- true: claim concerns the prospect's company, or a person clearly affiliated "
        "with it (executive, named successor, board member).\n"
        "- false: claim is about an unrelated entity merely sharing a name or keyword "
        "(e.g. a band, song, film, or a company in another industry).\n"
        'Reply with ONLY a JSON object: {"verdict": "valid"|"invalid"|"uncertain", '
        '"valence": "positive"|"neutral"|"soft_negative"|"sensitive", '
        '"about_prospect": bool, "reason": str} — reason is one short phrase (≤10 words).'
    )
    user_prompt = (
        f"Claim: {claim}\n\n"
        f"Source snippet: {source_snippet}\n\n"
        f"Prospect: {prospect_name}, {prospect_title} at {company_name}"
    )
    return system_prompt, user_prompt
