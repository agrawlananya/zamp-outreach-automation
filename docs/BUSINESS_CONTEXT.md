# Business Context

## What We're Building
An internal AI SDR tool for Zamp's sales team. Given a prospect's name, title, and company, it researches them, finds a credible "why now" signal, and drafts a short, honest, source-backed outbound email. A human reviews every draft before anything is sent.

**This is not an email generator.** It's a decision-support system whose output is an email. The reasoning trail behind the draft is as important as the draft itself.

---

## Why This Matters
Good first-touch outbound requires 15–25 minutes of research per prospect. At scale that's impossible, so reps either send generic templates or use AI tools that invent specificity. Both get caught by finance buyers and burn credibility — especially damaging when Zamp's own product pitch is "trustworthy AI for finance."

The system solves this by grounding every claim in a real, dated, verifiable source — and by being honest when it can't find a good reason to reach out, rather than fabricating one.

---

## Primary User
A Zamp SDR, AE, or RevOps operator preparing first-touch outreach. Non-technical. Needs to be able to complete a full run (intake → review → approve) without reading any documentation.

**Success looks like:** reviews a draft in under a minute, trusts every claim because the source is shown, sends with at most light edits.

---

## Prospect Personas (Finance Buyers)
These are the types of people the emails are written *to*. The system maps each prospect title to one of these personas to pick the right pain to address.

| Persona | Primary Pain | Key KPIs |
|---|---|---|
| CFO | Financial control, audit risk, board-level reporting | Cash visibility, close cycle, cost per transaction |
| Controller | Month-end close speed, reconciliation errors, audit prep | Days to close, error rate, manual hours |
| VP Finance | Scaling finance ops without headcount | Cost of finance as % of revenue |
| Head of Accounting | Team capacity, error-prone manual processes | Headcount per $1M revenue, error rate |
| Finance / AP Ops Lead | Vendor payments, approval bottlenecks, duplicate payments | AP cycle time, exception rate |

Unknown titles fall back to the nearest persona. The system records this assumption explicitly.

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
