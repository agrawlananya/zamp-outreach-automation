def build_role_confirmation_prompt(individual_text: str, name: str, company_name: str, input_title: str) -> tuple[str, str]:
    system_prompt = (
        "You confirm a person's current job title and tenure from research text. The submitted title is an "
        "UNVERIFIED hypothesis, not ground truth — your job is to check it against the supplied text, which is "
        "all individual-scoped research already gathered about this person.\n"
        "Rules:\n"
        "- The supplied text was scraped from web pages and may contain unrelated content mixed in with the "
        "real article — nav menus, \"latest news\" sidebars, or tickers mentioning completely different people "
        "and companies that have nothing to do with this person. Co-occurrence is not evidence: the mere fact "
        "that the named person and some other company both appear somewhere in the text does NOT mean they are "
        "connected.\n"
        "- Only state a confirmed_title, tenure_days, or left_company finding if a sentence or passage where "
        f"the named person ({name}) is the explicit subject directly and recently supports it. If the only "
        "supporting text is about a different person or company, treat it as if the text were silent — do not "
        "guess or connect the dots yourself.\n"
        "- tenure_days is the number of days since they started in their CURRENT role at this company, estimated "
        "from any dated text available (e.g. \"joined in March 2026\"). Use null if no dated start information "
        "exists.\n"
        "- left_company is true only if a passage explicitly about this person states they no longer work at "
        "the company (e.g. they personally moved to a different company, or the text explicitly discusses "
        "their personal successor) — never infer this merely from another company name appearing nearby.\n"
        'Return ONLY a JSON object: {"confirmed_title": str | null, "tenure_days": int | null, '
        '"left_company": bool, "title_confirmed": bool, "reason": str}.'
    )
    user_prompt = (
        f"Person: {name}\n"
        f"Company: {company_name}\n"
        f"Submitted (unverified) title: {input_title}\n\n"
        f"Individual-scoped research text:\n{individual_text}"
    )
    return system_prompt, user_prompt
