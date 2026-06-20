# Stage 3 — Run List (new screen)

> **Fresh chat?** Attach `00-shared-context.md` first, then this file.
> 📎 **Provide:** screenshot of the **Run List** screen.
> **Depends on:** Stage 1, Stage 2.

**Goal:** A dense, scannable triage table at `run-list.html`.

**Files:** create `frontend/run-list.html` + `frontend/js/run-list.js`; add `getRuns` params in
`js/api.js` if needed.

**Data:** `GET /api/runs?per_page=…&status=…&sort=…` (enriched).
**Columns:** Prospect · Title · Company · Persona (+ **ASSUMED** pill when `persona_assumed`) ·
Status (badge) · Groundedness (score bar + `pct%` + `grounded/total`) · Depth
(`personalization_depth`) · Updated (relative time from `created_at`).
**Controls:** Search (client-side filter over name/company), Filter (status dropdown), Export
(optional client-side CSV), Sort, "N of M runs", pagination. Row click → `run.html?id={id}`.
Insufficient/failed rows get a subtle danger left-accent. Empty + loading states required.

**Screen-specific guardrails:** no Campaign column; groundedness as bar+%+X/Y (not a fake
score); persona shows ASSUMED tag not a %.

**Done when:** table matches the screenshot's structure re-skinned to tokens; sort/filter/search
work; row navigation works; 40px rows; `label-md` uppercase headers. Commit:
`feat(ui): Run List screen`.
