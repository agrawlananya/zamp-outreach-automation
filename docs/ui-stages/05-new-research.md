# Stage 5 — New Research (intake)

> **Fresh chat?** Attach `00-shared-context.md` first, then this file.
> 📎 **Provide:** screenshot of the **New Research** screen.
> **Depends on:** Stage 1.

**Goal:** Re-skin `index.html` intake into a centered card on the shell.

**Files:** modify `frontend/index.html` + `frontend/js/intake.js`.

**Layout:** centered card (~440px): eyebrow "PROSPECT INTAKE" (accent label), title "Research a
new prospect", subtitle "We scan public sources, extract signals, and draft only what we can
ground." Fields: Prospect Name; row of Title + Company; optional **Research source** dropdown
(the existing `fixture_id` select, relabeled). Primary **Start Research** button. Below the
card, a muted mono "8-stage pipeline: Intake › Web Research › Signal Extract › Validate ›
Persona › Hook Score › Draft › QA" hint. Keep the existing submit→`createProspect`→redirect to
`run.html?id={run_id}` flow and inline error box.

**Screen-specific guardrails:** the optional dropdown is **Research source** (fixtures), not
"Campaign".

**Done when:** intake still creates a run and redirects; fixtures still populate the dropdown;
fully tokenized. Commit: `feat(ui): New Research intake screen`.
