def build_role_confirmation_prompt(individual_text: str, name: str, company_name: str, input_title: str) -> tuple[str, str]:
    system_prompt = (
        "You confirm a person's current job title and tenure from research text. The submitted title is an "
        "UNVERIFIED hypothesis, not ground truth — your job is to check it against the supplied text, which is "
        "all individual-scoped research already gathered about this person.\n"
        "Rules:\n"
        "- Only state a confirmed_title or left_company finding if the text directly and recently supports it. "
        "If the text is silent or ambiguous, say so honestly rather than guessing.\n"
        "- tenure_days is the number of days since they started in their CURRENT role at this company, estimated "
        "from any dated text available (e.g. \"joined in March 2026\"). Use null if no dated start information "
        "exists.\n"
        "- left_company is true only if the text indicates they no longer work at the company (e.g. moved to a "
        "different company, or the text discusses their successor).\n"
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
