import json


def build_writer_prompt(
    hook_signal: dict,
    persona: dict,
    pain_mappings: list[dict],
    prospect_first_name: str,
    sender_name: str,
    sender_title: str,
    new_in_role: bool = False,
    banned_tokens: list[str] | None = None,
) -> tuple[str, str]:
    new_in_role_instruction = (
        "This person started in their current role less than 90 days ago. Hook on their NEW MANDATE / "
        "first 90 days in the role, never on past performance at this company before they held this role.\n"
        if new_in_role
        else ""
    )
    valence_instruction = (
        "This hook is a soft-negative signal (cost pressure, hiring freeze, missed targets, \"do more with "
        "less\" mandates). Tone must be matter-of-fact and empathetic, never celebratory. Never use these "
        f"words: {', '.join(banned_tokens)}.\n"
        if banned_tokens
        else ""
    )

    system_prompt = (
        f"You write a single cold outbound email for {sender_name} ({sender_title}) at Zamp.\n"
        "Use ONLY the validated signals provided; never invent facts.\n"
        'Tone: plain, direct, peer-to-peer. No "I hope this finds you well", no buzzwords, no hype.\n'
        "No em/en dashes anywhere; use commas or periods instead.\n"
        f"{new_in_role_instruction}"
        f"{valence_instruction}"
        "\n"
        "DERIVED_CONSEQUENCE: the raw hook signal is supporting context, not the headline. Write one "
        "sentence stating the downstream OPERATIONAL CONSEQUENCE of that signal for this persona's pain — "
        "the second-order effect they'll actually feel, not the event itself.\n"
        "\n"
        "BODY: write ONLY three core paragraphs (no greeting, no sign-off — those are added separately). "
        "Total 50-90 words across the three paragraphs:\n"
        "1. Hook: lead with the derived_consequence, not the raw event. Mention the raw event only briefly, "
        "as supporting context (1-2 sentences).\n"
        "2. Value: what Zamp does for their specific situation, plus one credibility point (1-2 sentences).\n"
        "3. CTA: exactly one question. It must be a low-friction, interest-based ask that offers a small "
        "piece of value. Do NOT ask for time, a call, a meeting, or a number of minutes. Good example: "
        "'want me to send a quick breakdown of what it'd handle at your stage?'\n"
        "\n"
        "FACT vs INFERENCE: return the body as a flat list of tagged sentences (body_sentences), each with "
        "a paragraph number (1, 2, or 3) and a type:\n"
        "- fact: a literal claim directly supported by the supplied hook signal or pain mapping data. May "
        "assert plainly.\n"
        "- inference: your own reasoning or causal bridge, not directly stated in the supplied data (e.g. "
        "what this usually means, a likely downstream effect). MUST be hedged with dismissible language "
        "(\"teams at this stage often find...\", \"this usually means...\") and must NEVER be phrased as a "
        "stated fact about this specific prospect.\n"
        "\n"
        "SUBJECT and SUBJECT_ALT: two distinct options, each:\n"
        "- all lowercase, 2-5 words, under 42 characters.\n"
        "- references the prospect's specific hook or creates a light curiosity gap.\n"
        "- must read like it was written by a human, not a campaign.\n"
        "- banned: exclamation marks, ALL CAPS, the words free/guarantee/demo/webinar, the company name "
        "used as a label, and clickbait phrasing.\n"
        "\n"
        "Return ONLY valid JSON, no markdown:\n"
        "{\n"
        '  "subject": "string",\n'
        '  "subject_alt": "string",\n'
        '  "derived_consequence": "string, one sentence",\n'
        '  "body_sentences": [{"paragraph": 1, "text": "string", "type": "fact" | "inference"}]\n'
        "}"
    )
    user_prompt = (
        f"Prospect first name: {prospect_first_name}\n\n"
        f"Hook signal:\n{json.dumps(hook_signal)}\n\n"
        f"Persona:\n{json.dumps(persona)}\n\n"
        f"Pain mappings:\n{json.dumps(pain_mappings)}"
    )
    return system_prompt, user_prompt
