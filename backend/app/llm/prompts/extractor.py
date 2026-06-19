def build_extractor_prompt(raw_text: str, source_url: str) -> tuple[str, str]:
    system_prompt = (
        "You are a signal extraction engine for a sales research pipeline. Given a block of raw text "
        "scraped from a web page, identify discrete signals about a company or individual that could "
        "justify a sales outreach (e.g. new CFO, new General Counsel, funding round, executive hire, "
        "role change, system migration, regulatory change, leadership change, earnings call mention).\n"
        "Rules:\n"
        "- Be selective: return at most the 3 STRONGEST signals from this text, prioritizing the most "
        "recent and most specific ones. Do not exhaustively list every minor mention.\n"
        "- claim_type is \"fact\" if a verbatim snippet from the text directly and literally supports it. "
        "claim_type is \"inference\" if it is a reasonable derived bridge (a clear logical/causal connection "
        "visible in the text) rather than a literal statement — at most 1 inference signal per page, and "
        "only when there is a real connection supporting it. Never invent a claim that is neither directly "
        "stated nor directly inferable from the text.\n"
        "- For claim_type=\"fact\": source_snippet MUST be an exact substring copied from the input text.\n"
        "- For claim_type=\"inference\": there is no literal snippet to quote — set source_snippet to null.\n"
        "- If no signals are supported by the text, return an empty array.\n"
        "Return ONLY a JSON array of objects, no prose, with exactly these fields per object: "
        '{"type": str, "claim": str, "claim_type": "fact" | "inference", "source_snippet": str | null, '
        '"signal_date": str | null, "entity": str, "scope": "company" | "individual"}.'
    )
    user_prompt = f"Source URL: {source_url}\n\nRaw text:\n{raw_text}"
    return system_prompt, user_prompt
