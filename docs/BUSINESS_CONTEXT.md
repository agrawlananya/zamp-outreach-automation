# Business Context

## What We're Building
An internal AI SDR tool for Zamp's sales team. Given a prospect's name, title, and company, it researches them, finds a credible "why now" signal, and drafts a short, honest, source-backed outbound email. A human reviews every draft before anything is sent.

**This is not an email generator.** It's a decision-support system whose output is an email. The reasoning trail behind the draft is as important as the draft itself.

---

## Why This Matters
Good first-touch outbound requires 15–25 minutes of research per prospect. At scale that's impossible, so reps either send generic templates or use AI tools that invent specificity. Both get caught by buyers and burn credibility — especially damaging when Zamp's own product pitch is trustworthy, autonomous AI execution. Zamp is an AI employee platform, not a finance-only tool: finance and accounting are the flagship wedge, but the same model — brief it once, it runs the job end-to-end, escalating only true exceptions — extends to legal, sales, marketing, product, procurement, compliance, RevOps, support, recruiting, and data ops.

The system solves this by grounding every claim in a real, dated, verifiable source — and by being honest when it can't find a good reason to reach out, rather than fabricating one.

---

## Primary User
A Zamp SDR, AE, or RevOps operator preparing first-touch outreach. Non-technical. Needs to be able to complete a full run (intake → review → approve) without reading any documentation.

**Success looks like:** reviews a draft in under a minute, trusts every claim because the source is shown, sends with at most light edits.

---

## Prospect Personas
These are the types of people the emails are written *to*. The system maps each prospect title to one of these personas to pick the right pain to address. Personas span both **economic buyers** (budget authority — CFO, CEO, CRO, General Counsel, etc.), **functional buyers** (own the workflow — VP Finance, Head of Legal Ops, VP Marketing, etc.), and **managers** (day-to-day operators and champions — Controller, AP Manager, Recruiting Manager, etc.).

Personas now cover every function Zamp's AI-employee model applies to, not just finance:

- Executive / Founder / Board
- Finance & Accounting (flagship wedge)
- Procurement
- Compliance & Risk
- Legal
- Marketing
- Sales
- IT & Technology
- Cybersecurity
- Product & Engineering
- RevOps & GTM
- Customer Success & Support
- Recruiting & People Ops
- Data Operations
- Operations (cross-functional)

The full persona library — title aliases, goals, pains, KPIs, and messaging angle per persona — lives in `backend/app/services/persona_library.py`. Unknown titles fall back to the nearest persona via an LLM match. The system records this assumption explicitly (`is_assumed`).

---

## Run Outcomes
Every run ends in exactly one status:

| Status | Meaning |
|---|---|
| `ready_for_review` | Strong signal found, draft generated, groundedness passed |
| `insufficient_signal` | Top hook score < 0.45 — shows honest fallback, not a fake-personal draft |
| `needs_human_research` | Draft generated but failed groundedness check after 1 retry |
| `deprioritized` | Prospect doesn't match Zamp's ICP |
| `failed` | Unrecoverable pipeline error after retries |

The system **must not** generate a confident-looking personalized draft when it doesn't have the signal to back it up.

---

## What "Groundedness" Means
Every factual claim in a sent draft must map to a stored, validated signal with a real source URL and verbatim snippet. The groundedness score is:

> (claims traceable to a validated signal) / (total factual claims in draft)

Target: **100%** on every `ready_for_review` draft. A draft that fails this check is regenerated once, then escalated. It is never silently sent.

---

## North Star Metrics (Dashboard)
1. **Human Acceptance Rate** — % of drafts approved (as-is or with edits)
2. **Groundedness %** — % of claims backed by a source
3. **Escalation Rate** — % of runs routed to `insufficient_signal` or `needs_human_research`
4. **Avg. Time-to-Draft** — pipeline wall-clock time
5. **Personalization Depth** — 0 (generic) / 1 (company signal) / 2 (individual signal)

---

## Out of Scope for V1
- Multi-touch email sequences
- CRM write-back
- Bulk / CSV prospect import
- Multi-user roles or permissions
- Self-improving model that retrains on feedback
