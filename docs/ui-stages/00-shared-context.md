# Shared Context — attach to EVERY stage chat

> Paste/attach this file first in any fresh chat, then attach the stage file (e.g.
> `03-run-list.md`) and the screen's screenshot.

## Product & hard constraints
**Zamp AI SDR** is an internal decision-support tool: given a prospect (name, title, company)
it researches them and drafts a grounded, source-backed outbound email with a fully visible
reasoning trail. A human reviews every draft. Trust > decoration; every claim must trace to a
stored signal.

**Hard constraints (do not violate):**
- **Do NOT change core logic.** Off-limits: `backend/app/pipeline/**`, `backend/app/llm/**`,
  `backend/app/services/scoring.py`, `backend/app/services/persona_library.py`, and
  `backend/app/models/db_models.py` (**no DB schema changes**). Only read-side/data-fetch and
  frontend code may change.
- **Frontend is plain HTML/CSS/JS.** No frameworks, no bundler, no build step. Vanilla
  `fetch()`. Poll `/api/runs/{id}/status` every 1.5s while a run is in progress.
- **Light mode only** for this redesign. (`DESIGN.md` defines no dark palette.)
- **Honesty/groundedness is the product.** Never render a feature or number the backend can't
  back. See Guardrails.
- `DESIGN.md` at repo root is the **authoritative** design system — read it. Token essentials
  are embedded below for convenience.

## Repo map (where things live)
```
frontend/
  index.html      New Research (intake)            run.html   live run + review (state-driven)
  dashboard.html  Performance Dashboard            css/style.css
  js/api.js  js/intake.js  js/run-view.js  js/dashboard.js
backend/app/
  api/prospects.py runs.py drafts.py metrics.py     models/schemas.py  models/db_models.py
  services/  pipeline/  llm/                         db/
docs/BUSINESS_CONTEXT.md   DESIGN.md   UI_REDESIGN_PLAN.md   docs/ui-stages/
```
Run backend: `cd backend && uvicorn app.main:app --reload --port 8000`
Serve frontend: from `frontend/` → `python -m http.server 5500` (API base in `js/api.js` is `http://localhost:8000`).
Tests: `cd backend && pytest tests/ -v`.

## Design tokens (DESIGN.md — authoritative; drop this into `frontend/css/tokens.css`)
```css
:root{
  /* brand */
  --color-ink:#16171A; --color-accent:#2347E5; --color-accent-hover:#1A38C4; --color-accent-subtle:#EBF0FD;
  --color-mist:#ECEEF3; --color-paper:#FFFFFF; --color-raised:#E4E7EF;
  --color-border:#ECEEF3; --color-border-strong:#C8CCDA;
  --text-primary:#16171A; --text-secondary:#5B5E66; --text-muted:#9396A0;
  /* semantic status (text / bg) */
  --success:#16A34A; --success-bg:#F0FDF4; --warning:#D97706; --warning-bg:#FFFBEB;
  --danger:#DC2626;  --danger-bg:#FEF2F2;  --info:#2347E5;    --info-bg:#EBF0FD;
  --neutral:#5B5E66; --neutral-bg:#ECEEF3;
  /* sidebar (always dark) */
  --sidebar-bg:#16171A; --sidebar-text:#9396A0; --sidebar-text-active:#FFFFFF; --sidebar-active-bg:#2C2D32;
  /* trust signals */
  --snippet-bg:#E4E7EF; --snippet-border:#C8CCDA; --score-high:#16A34A; --score-mid:#D97706; --score-low:#DC2626;
  /* radii */ --radius-sm:4px; --radius-md:6px; --radius-lg:8px; --radius-xl:12px; --radius-full:9999px;
  /* spacing — 8px grid */ --space-xs:4px; --space-sm:8px; --space-md:16px; --space-lg:24px; --space-xl:32px; --space-2xl:48px;
  --sidebar-width:240px; --topbar-height:56px; --card-padding:24px; --row-height:40px; --gutter:24px; --max-content:1280px;
  /* type */ --font-sans:'Inter',system-ui,sans-serif; --font-mono:'JetBrains Mono',ui-monospace,monospace;
}
```
**Type scale (Inter):** display 24/500/-0.02em · headline-lg 20/500 · headline-md 16/500 ·
headline-sm 14/500 (buttons, th, active nav) · body-lg 15/400/1.6 · body-md 14/400/1.6 ·
body-sm 13/400 · label-md 12/500 UPPERCASE 0.06em (table headers) · label-sm 11/500 UPPERCASE
0.08em (badges). **Mono (JetBrains Mono) ONLY for source snippets (13/400/1.6) and the email
draft body (14/400/1.7).** Load both fonts via Google Fonts `<link>`.
**Shape/elevation:** buttons/inputs `--radius-md`, cards `--radius-lg`, banners `--radius-xl`,
pills `--radius-full` (badges only). Depth via tonal layers + 1px borders, **no drop shadows**
(except dropdown/tooltip `0 4px 12px rgba(0,0,0,.08)`). Cards never nest in cards.
**Buttons:** primary = accent fill/white; secondary = paper + `--color-border-strong`; success
= green fill (**Approve only**); danger = paper + danger border/text (**Reject only**). Button
labels are sentence-case `headline-sm`, never ALL CAPS.

## Guardrails — strip/adapt from EVERY screenshot
| In the mockup | Do this instead |
|---|---|
| "Approve & Send", "Sent via Outreach.io" | **No send/CRM.** Button is **Approve** (green, success); show "Approved" + **Copy**, never "Sent". |
| To / From email rows on the draft | **Drop.** No email field exists. Show "Recipient: {name} · {title}, {company}". |
| Persona "94% confidence" | **No confidence score.** Use `persona_mapping.is_assumed` → an **ASSUMED** pill (no %). |
| "System Resources" (compute/memory), streaming fake logs | **Drop.** Optional real "View Logs" = `audit_log` (stage/status/latency) only. |
| Metric trend arrows (↑3% / ↓1%) | **Drop.** Show real sub-counts only ("156 of 200 reviewed", "47/50 drafts"). |
| "Campaign" field/column | **Drop.** Reuse the optional intake slot for the existing `fixture_id` → relabel "Research source". |
| "Pause" / "Override Threshold" / "Mark as Dead" | **Drop.** Only real recovery = **Retry** (`POST /api/runs/{id}/retry`, failed runs only). |
| Prospects / Campaigns / Settings nav | **Drop.** Sidebar = New Research, Dashboard, Run List only. |
| IBM Plex / indigo / dark theme | Re-skin to `DESIGN.md`: Inter + JetBrains Mono, accent `#2347E5`, **Ink sidebar**, Mist page, light only. |

## Backend data contract (what the UI may consume)
- `POST /api/prospects` ← `{name, title, company_name, fixture_id?}` → `{run_id}`
- `GET /api/fixtures` → `{fixture_ids: string[]}`
- `GET /api/runs/{id}/status` → `{status, current_stage, percent_complete}` (poll this @1.5s)
- `GET /api/runs/{id}` → **RunDetailResponse**:
  ```
  id, prospect_id, status, current_stage, started_at, completed_at, time_to_draft_ms,
  escalation_reason, fixture_id, is_fixture,
  signals: [{ id, scope("company"|"individual"), type, claim, source_url, source_snippet,
              signal_date, entity, validated, validation_reason,
              relevance_score, specificity_score, recency_score, actionability_score,
              verifiability_score, hook_score, adjusted_hook_score, selected_as_hook,
              valence, saturation, claim_type("fact"|"inference") }],
  persona_mapping: { persona_name, is_assumed, goals, pains, kpis },   // goals/pains/kpis are JSON-string arrays
  pain_mappings: [{ signal_id, owned_pain, owned_kpi, zamp_value_prop }],
  role_confirmation: { input_title, confirmed_title, tenure_days, title_corrected,
                       title_assumed, new_in_role, left_company },
  draft: { id, version, subject, subject_alt, body, sources_used, rubric_scores,
           groundedness_pass, derived_consequence, body_sentences, created_at },
           // sources_used / rubric_scores / body_sentences are JSON strings.
           // body_sentences = [{ paragraph, text, type:"fact"|"inference", signal_id }]
  audit_log: [{ stage, status("ok"|"degraded"|"failed"), latency_ms, model_used,
                input_snapshot, output_snapshot, error_message, created_at }]
  ```
- `GET /api/runs?status=&page=&per_page=` → `{items:[...], page, per_page, total}`.
  **Current** item: `{id, prospect_name, company, status, top_hook_score, time_to_draft_ms, human_decision, created_at}`.
  **After Stage 2** also: `title, persona_name, persona_assumed, groundedness_pct,
  groundedness_grounded, groundedness_total, personalization_depth, signal_type, signal_source_domain`.
- `GET /api/metrics` → `{acceptance_rate, groundedness_pct, escalation_rate,
  avg_time_to_draft_ms, avg_personalization_depth}` (+ optional sub-counts from Stage 2).
- `PATCH /api/drafts/{id}/review` ← `{action:"approve"|"approve_with_edits"|"reject", edited_body?, reason?}` → `{ok}`
- `POST /api/runs/{id}/retry` → `{new_run_id}` (400 unless run status is `failed`).

## Existing frontend (reuse — do not rewrite the logic)
- `js/api.js` exports: `getFixtures()`, `createProspect(data)`, `getRunStatus(id)`, `getRun(id)`,
  `getRuns(params)`, `retryRun(id)`, `submitReview(draftId, payload)`, `getMetrics()`.
- `js/run-view.js`: polls every `POLL_INTERVAL_MS = 1500`; renders live stages + review; keeps
  the **two-click confirm** UX for "Approve with Edits" and "Reject", and a **Retry** button on
  failures. Preserve these behaviors.
- `js/dashboard.js`: loads metrics + runs, sortable headers, status filter, row → `run.html?id=`.
- `js/intake.js`: loads fixtures into the select, submits, redirects to `run.html?id=`.

## Mappings
**Pipeline (backend 11 stages → 8 UI rows):** 1 Intake & Parsing = `stage1_intake`
(+`stage3_role_confirmation`) · 2 Web Research = `stage2_research` · 3 Signal Extraction =
`stage4_extract_signals` · 4 Signal Validation = `stage5_validate_signals` · 5 Persona & Pain
Mapping = `stage6_persona_mapping`+`stage7_pain_mapping` · 6 Hook Scoring & Selection =
`stage8_hook_scoring` · 7 Draft Generation = `stage9_draft_generation` · 8 Quality Check &
Scoring = `stage10_quality_scoring` (+`stage11_routing`). State/elapsed from `audit_log`
(`status`, `latency_ms`) + `run.current_stage`.

**Status → badge:** `ready_for_review`→**READY** (success) · `running`→**RUNNING** (info,
pulsing dot) · `insufficient_signal`→**INSUFFICIENT SIGNAL** (warning) ·
`needs_human_research`→**NEEDS RESEARCH** (warning/danger) · `reviewed`→**REVIEWED** (neutral;
or APPROVED if the review action was approve) · `failed`→**FAILED** (danger) ·
`deprioritized`→**DEPRIORITIZED** (neutral). Badges: pill, `label-sm` UPPERCASE, color-matched
tint. Score bars: 4px tall, full-radius, colored by threshold (≥.7 high / .45–.69 mid / <.45
low), **always shown with the numeric value**.

## Global Definition of Done (every stage)
- Re-skinned to `DESIGN.md` tokens (via `tokens.css` vars); no IBM Plex/indigo/dark leftovers.
- No dropped feature reintroduced (check the Guardrails table).
- All states designed where applicable: loading / empty / error / degraded / success.
- Reasoning trail stays **co-equal** with the draft (never a footnote).
- Source snippets always show domain + URL above them; mono font; never unattributed.
- No console errors; existing flows still work; `pytest` green if backend touched.
- Commit at the end with a clear message (one stage = one commit).

## Per-stage workflow
1. Read `DESIGN.md` + the files named in the stage. 2. Implement. 3. Verify against the
screenshot + acceptance criteria. 4. Commit.
