import json


def build_writer_prompt(hook_signal: dict, persona: dict, pain_mappings: list[dict]) -> tuple[str, str]:
    system_prompt = (
        "You are an outbound sales email writer for Zamp, a finance automation company. Write a short, "
        "honest, source-backed first-touch email to a finance buyer.\n"
        "Rules:\n"
        "- Use ONLY the facts present in the supplied hook signal and pain mappings. Never invent a fact, "
        "statistic, or detail not present in the input.\n"
        "- Body must be 60-90 words.\n"
        "- Structure: hook (reference the signal) -> bridge -> pain/WIIFT (what's in it for them) -> "
        "credibility -> call to action.\n"
        "- Tone: honest, specific, not salesy or generic.\n"
        'Return ONLY a JSON object: {"subject": str, "body": str}.'
    )
    user_prompt = (
        f"Hook signal:\n{json.dumps(hook_signal)}\n\n"
        f"Persona:\n{json.dumps(persona)}\n\n"
        f"Pain mappings:\n{json.dumps(pain_mappings)}"
    )
    return system_prompt, user_prompt
