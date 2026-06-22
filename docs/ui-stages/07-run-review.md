# Stage 7 — run.html: Review state (Review Draft)

> **Fresh chat?** Attach `00-shared-context.md` first, then this file.
> 📎 **Provide:** screenshot of the **Review Draft** screen.
> **Depends on:** Stage 1 (Stage 6 shares the page).

**Goal:** The human gate — two-column **co-equal** review.

**Files:** modify `frontend/run.html` + `frontend/js/run-view.js`.

**Left — Generated Draft card:** "GENERATED DRAFT" label + groundedness pill
(`grounded/total` + `pct%` via `groundedness_ratio` logic, or derive client-side from
`body_sentences`); editable Subject; body in **mono** (`--font-mono`) with inline citation
markers `S1/S2…` rendered from `body_sentences[].signal_id` (map each used signal to an index).
Actions: **Reject** (danger outline) · **Approve with Edits** (secondary) · **Approve**
(success green). Keep the existing two-click confirm for Reject / Approve-with-Edits; call
`submitReview(draftId, …)`.

**Right — Reasoning Trail (co-equal heading):**
- **Web Research:** one source card per cited signal — `S#` + domain + URL link + mono snippet.
- **Hook Scoring:** caption "5 axes → REL · SPEC · REC · ACT · VER. HOOK = weighted composite."
  Then each candidate signal: claim + flag (✓ SELECTED / considered / low-recency) + HOOK score
  + a score bar + the five sub-scores (`relevance/specificity/recency/actionability/
  verifiability_score`). Selected = `selected_as_hook`.
- Collapsible sub-sections: **Persona Match** (`persona_mapping`: name + ASSUMED + goals/pains/
  kpis), **Draft Generation** (`derived_consequence` / framework), **Groundedness Check** (list
  of grounded claims with their sources).

**Screen-specific guardrails:** button is **Approve** (no "& Send"); no To/From email rows.

**Done when:** review renders from `GET /api/runs/{id}`; inline citations line up with sources;
5-axis scores + bars show numeric values; approve/edit/reject post correctly and lock the UI.
Commit: `feat(ui): review draft (two-column, hook scoring + citations)`.
