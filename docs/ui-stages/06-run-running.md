# Stage 6 — run.html: Running state (Research Progress)

> **Fresh chat?** Attach `00-shared-context.md` first, then this file.
> 📎 **Provide:** screenshot of the **Research Progress** (live run) screen.
> **Depends on:** Stage 1.

**Goal:** Redesign the in-progress view in `run.html`/`run-view.js`. Keep the 1.5s polling.

**Files:** modify `frontend/run.html` + `frontend/js/run-view.js`.

**Layout:** status header — initials avatar, prospect name, **RUNNING** badge (pulsing dot),
`title · company · persona`; right side `Stage X of 8` + optional **View Logs**. Two-column:
left **Execution Pipeline** card (8 grouped rows; each row = status icon (done ✓ / active ● /
queued ○ / degraded ▲) + name + elapsed/summary; active row gets a 2px accent left border and
expands to show Matched Persona (name + **ASSUMED** if assumed) + KPIs + Pain Points from
`persona_mapping`); right **Contextual Signals** card (source cards from `signals`: label +
domain + mono snippet). Map stages per Shared Context; pull state/elapsed from `audit_log` +
`current_stage`.

**Screen-specific guardrails:** **drop** System Resources, persona %, fake streaming logs, and
Pause. "View Logs" (if kept) shows only real `audit_log` entries.

**Done when:** polling advances stage states live; active stage detail renders from real data;
terminal status switches the page to the right state (review/reviewed/error). Commit:
`feat(ui): live run (Research Progress) view`.
