from app.llm.client import call_llm

PERSONAS: dict[str, dict] = {
    "cfo": {
        "name": "CFO",
        "goals": ["Maintain financial control", "Reduce audit risk", "Deliver clean board-level reporting"],
        "pains": ["Financial control gaps", "Audit risk", "Board-level reporting pressure"],
        "kpis": ["Cash visibility", "Close cycle", "Cost per transaction"],
        "messaging_angle": "Position Zamp as the trustworthy AI layer that strengthens financial control and audit readiness.",
        "zamp_value_prop": "Zamp gives CFOs verifiable, source-backed financial visibility without adding audit risk.",
    },
    "controller": {
        "name": "Controller",
        "goals": ["Speed up month-end close", "Reduce reconciliation errors", "Stay audit-ready year round"],
        "pains": ["Month-end close speed", "Reconciliation errors", "Audit prep burden"],
        "kpis": ["Days to close", "Error rate", "Manual hours"],
        "messaging_angle": "Position Zamp as the way to compress close cycles and cut manual reconciliation work.",
        "zamp_value_prop": "Zamp automates reconciliation and close tasks so Controllers close faster with fewer errors.",
    },
    "vp finance": {
        "name": "VP Finance",
        "goals": ["Scale finance operations without adding headcount"],
        "pains": ["Scaling finance ops without headcount"],
        "kpis": ["Cost of finance as % of revenue"],
        "messaging_angle": "Position Zamp as the lever that lets finance scale output without scaling headcount.",
        "zamp_value_prop": "Zamp lets VPs of Finance absorb growth in transaction volume without proportional headcount growth.",
    },
    "head of accounting": {
        "name": "Head of Accounting",
        "goals": ["Increase team capacity", "Eliminate error-prone manual processes"],
        "pains": ["Team capacity constraints", "Error-prone manual processes"],
        "kpis": ["Headcount per $1M revenue", "Error rate"],
        "messaging_angle": "Position Zamp as the way to multiply team capacity by removing manual, error-prone work.",
        "zamp_value_prop": "Zamp automates manual accounting workflows, freeing the team to focus on higher-value work.",
    },
    "finance/ap ops lead": {
        "name": "Finance/AP Ops Lead",
        "goals": ["Streamline vendor payments", "Remove approval bottlenecks", "Eliminate duplicate payments"],
        "pains": ["Vendor payment friction", "Approval bottlenecks", "Duplicate payments"],
        "kpis": ["AP cycle time", "Exception rate"],
        "messaging_angle": "Position Zamp as the way to remove AP bottlenecks and duplicate-payment risk.",
        "zamp_value_prop": "Zamp speeds up AP cycle time and catches duplicate/exception payments before they go out.",
    },
}


def lookup_persona(title: str) -> tuple[dict, bool]:
    key = title.strip().lower()
    if key in PERSONAS:
        return PERSONAS[key], False

    names = [p["name"] for p in PERSONAS.values()]
    system_prompt = (
        "You map a job title to the closest matching finance persona from a fixed list. "
        "Respond with ONLY the exact persona name from the list, nothing else."
    )
    user_prompt = f"Job title: {title}\n\nPersona list: {', '.join(names)}"
    response = call_llm(system_prompt, user_prompt, temperature=0.1, max_tokens=20)
    matched_name = response.strip().lower()

    for persona in PERSONAS.values():
        if persona["name"].lower() == matched_name:
            return persona, True

    for persona in PERSONAS.values():
        if persona["name"].lower() in matched_name or matched_name in persona["name"].lower():
            return persona, True

    return PERSONAS["cfo"], True
