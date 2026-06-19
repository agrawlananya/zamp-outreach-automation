def build_extractor_prompt(raw_text: str, source_url: str) -> tuple[str, str]:
    system_prompt = (
        "You are a signal extraction engine for a sales research pipeline. Given a block of raw text "
        "scraped from a web page, identify discrete, factual signals about a company or individual that "
        "could justify a sales outreach (e.g. new CFO, new General Counsel, funding round, executive hire, "
        "role change, system migration, regulatory change, leadership change, earnings call mention).\n"
        "Rules:\n"
        "- Be selective: return at most the 3 STRONGEST signals from this text, prioritizing the most "
        "recent and most specific ones. Do not exhaustively list every minor mention.\n"
        "- Only emit a signal if a verbatim snippet from the provided text directly supports it.\n"
        "- Never infer, assume, or extrapolate beyond what is literally stated in the text.\n"
        "- source_snippet must be an exact substring copied from the input text.\n"
        "- If no signals are supported by the text, return an empty array.\n"
        "Return ONLY a JSON array of objects, no prose, with exactly these fields per object: "
        '{"type": str, "claim": str, "source_snippet": str, "signal_date": str | null, "entity": str, '
        '"scope": "company" | "individual"}.'
    )
    user_prompt = f"Source URL: {source_url}\n\nRaw text:\n{raw_text}"
    return system_prompt, user_prompt
