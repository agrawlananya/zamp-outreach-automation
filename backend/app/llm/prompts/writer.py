import json


def build_writer_prompt(
    hook_signal: dict,
    persona: dict,
    pain_mappings: list[dict],
    prospect_first_name: str,
    sender_name: str,
    sender_title: str,
) -> tuple[str, str]:
    system_prompt = (
        f"You write a single cold outbound email for {sender_name} ({sender_title}) at Zamp.\n"
        "Use ONLY the validated signals provided; never invent facts.\n"
        'Tone: plain, direct, peer-to-peer. No "I hope this finds you well", no buzzwords, no hype.\n'
        "No em/en dashes anywhere; use commas or periods instead.\n"
        "\n"
        "BODY: write ONLY the three core paragraphs below (no greeting, no sign-off — those are added "
        "separately). Total 50-90 words across the three paragraphs, separated by \\n\\n:\n"
        "1. Hook: reference the supplied signal specifically (1-2 sentences).\n"
        "2. Value: what Zamp does for their specific situation, plus one credibility point (1-2 sentences).\n"
        "3. CTA: exactly one question. It must be a low-friction, interest-based ask that offers a small "
        "piece of value. Do NOT ask for time, a call, a meeting, or a number of minutes. Good example: "
        "'want me to send a quick breakdown of what it'd handle at your stage?'\n"
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
        '  "body": "string, the three paragraphs only, separated by \\n\\n"\n'
        "}"
    )
    user_prompt = (
        f"Prospect first name: {prospect_first_name}\n\n"
        f"Hook signal:\n{json.dumps(hook_signal)}\n\n"
        f"Persona:\n{json.dumps(persona)}\n\n"
        f"Pain mappings:\n{json.dumps(pain_mappings)}"
    )
    return system_prompt, user_prompt
