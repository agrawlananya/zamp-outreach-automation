# Zamp AI SDR — Frontend Redesign Analysis & Plan

## Context
The current frontend (`frontend/index.html`, `run.html`, `dashboard.html` + vanilla JS) works but is visually ad‑hoc: a top‑nav header, ad‑hoc CSS variables (`--bg-dark`, `--blue`…), and a flat reasoning trail. A new set of 6 screens was designed in **Claude Design** (project `1ac8e687-…` "Zamp Sales Email Decision Tool", source file `Zamp AI SDR Screens.dc.html` + `Sidebar.dc.html`). This document analyzes what must change in the **frontend**, **backend (data‑fetch only)**, and **database** to adopt those screens — re‑skinned to the canonical tokens in `DESIGN.md`, and filtered against the real product scope in `docs/BUSINESS_CONTEXT.md`.

**Hard constraint:** do **not** change core pipeline logic (the 11 stages, signal extraction/validation, hook scoring, draft generation, quality/groundedness, routing). Only read‑side/data‑fetch logic may change.

## Source‑of‑truth screens (Claude Design, fetched via `DesignSync`)
| # | Screen | Maps to | Layout highlights |
|---|--------|---------|-------------------|
| 01 | **Run List** | NEW `run-list.html` | Dense table: Prospect · Title·Company · Persona(+ASSUMED) · Status · Groundedness(bar+%+X/Y) · Depth · Updated. Search/Filter/Export, "6 of 124", sort. |
| 02 | **New Research** | `index.html` | Centered intake card: eyebrow "Prospect Intake", Name, Title+Company, optional dropdown, "Start Research", 8‑stage pipeline hint. |
| 03 | **Research Progress** (live run) | `run.html` (running) | Status header (name, RUNNING, title·company·persona), "Execution Pipeline" (8 grouped stages, done/active/queued + elapsed), active stage expands (persona/pains/KPIs), Contextual Signals. |
| 04 | **Review Draft** | `run.html` (review) | **Two‑column co‑equal**: left Generated Draft (subject, body w/ inline citations, groundedness 3/3, Reject/Approve‑with‑Edits/Approve); right Reasoning Trail (Web Research source cards, 5‑axis Hook Scoring table, Persona/Draft/Groundedness collapsibles). |
| 05 | **Post‑Approval** | `run.html` (reviewed) | "Approval Confirmed" banner + decision record, locked read‑only draft + Copy, archived reasoning trail. |
| 06 | **Performance Dashboard** | `dashboard.html` | 5 metric cards + "Recent Runs" mini‑table. |

## Guardrails — design elements NOT backed by product/backend (drop or adapt)
The mockups contain plausible‑looking but unsupported content. Adapting these is required to keep the product honest (its entire value is groundedness):
- **"Approve & Send" / "Sent via Outreach.io"** → rename to **"Approve" / "Confirm & Approve"**; no send/CRM integration exists and it is explicitly out of V1 scope. Post‑Approval shows "Approved" + Copy, not "Sent".
- **To / From email fields** on the draft → drop (no email/recipient field on `prospects`/`drafts`). Show prospect name/company only.
- **Persona "94% confidence"** → there is no confidence score; map to the real `persona_mapping.is_assumed` → an **ASSUMED** tag (omit a numeric %).
- **"System Resources" (compute node / memory)** and **streaming "SEC filings…" logs** → drop; not produced by the backend. Optional: a "View Logs" affordance can surface the real `audit_log` (stage/status/latency).
- **Metric trend arrows (↑3% / ↓1%)** → drop; no historical/period store exists (fabricating trends violates the trust principle). Real sub‑counts ("156 approvals", "47/50 verified") are derivable and may be shown.
- **"Campaign" field/column** → drop (no campaign model; out of V1 scope). Reuse that optional intake slot for the existing `fixture_id` ("Research source") control instead.
- **"Pause" / "Override Threshold" / "Mark as Dead"** buttons → drop (no endpoints). The only real recovery action is **Retry** (`POST /api/runs/{id}/retry`, failed runs only).
- **Prospects / Campaigns / Settings** nav → excluded; sidebar is New Research, Dashboard, Run List only.

## Design‑token reconciliation (Claude Design spec → `DESIGN.md` token)
Implement the new layouts but bind them to `DESIGN.md` tokens (the canonical DS). Build **light mode only** for v1 ("Daylight"); the "Console" dark theme is a deferred extension (`DESIGN.md` defines no dark palette).
| Concern | Claude Design value | Use instead (`DESIGN.md`) |
|---|---|---|
| Sans font | IBM Plex Sans | **Inter** (`typography.*`) |
| Mono font (snippets, email, labels, scores) | IBM Plex Mono | **JetBrains Mono** (`mono`, `email-body`) |
| Accent | indigo `#5b54e6` / `#4b44d6` | **Accent `#2347E5`** (`primary`), hover `#1A38C4`, subtle `#EBF0FD` |
| Sidebar bg | light `#fbfbfc` (daylight) | **Ink `#16171A`** (`sidebar-bg`) — sidebar is always dark per DS |
| Page bg | `#e8e7e3` / `#fcfcfd` | **Mist `#ECEEF3`** (`neutral`) |
| Card / surface | `#ffffff` + soft shadow | **Paper `#FFFFFF`**, 1px Mist border, no shadow (tonal only) |
| Snippet block | tinted card | **`snippet-bg #E4E7EF`** + `snippet-border #C8CCDA`, mono |
| Status green/amber/red/grey/blue | various | `status-success/-warning/-danger/-neutral/-info` (+ `*-bg`) |
| Radii | 9–12px | cards `lg 8px`, buttons/inputs `md 6px`, banners `xl 12px`, badges `full` |
| Approve button | dark fill | **`button-success` green** (approve only); Reject = `button-danger` outline |
| Score bars | colored bars | `score-bar-high/-mid/-low` (green ≥.7 / amber .45–.69 / red <.45) |
| Status badges | rounded chips | pill `rounded.full`, `label-sm` uppercase, color‑matched tints |

**Stage mapping** (backend 11 stages → UI's 8 "Execution Pipeline" rows): 1 Intake & Parsing = `stage1_intake` (+`stage3_role_confirmation` folded in); 2 Web Research = `stage2_research`; 3 Signal Extraction = `stage4_extract_signals`; 4 Signal Validation = `stage5_validate_signals`; 5 Persona & Pain Mapping = `stage6_persona_mapping`+`stage7_pain_mapping`; 6 Hook Scoring & Selection = `stage8_hook_scoring`; 7 Draft Generation = `stage9_draft_generation`; 8 Quality Check & Scoring = `stage10_quality_scoring` (+`stage11_routing`). Stage state/elapsed comes from `audit_log` (`status` ok/degraded/failed, `latency_ms`) and `run.current_stage`.

**Status → badge mapping** (real 7 statuses): `ready_for_review`→READY/COMPLETED (success), `running`→RUNNING (info, pulsing dot), `insufficient_signal`/`needs_human_research`→INSUFFICIENT SIGNAL / NEEDS RESEARCH (warning/danger), `reviewed`→REVIEWED/APPROVED (neutral/success per action), `failed`→FAILED (danger), `deprioritized`→DEPRIORITIZED (neutral). (`deprioritized` is documented in BUSINESS_CONTEXT; render it if the backend emits it — do not add emission logic.)

## Database schema — **no changes required**
Every field the new screens need is already persisted:
- Run List columns: `prospects.title`, `persona_mappings.persona_name`+`is_assumed`, per‑run groundedness (derived), personalization depth (derived), `runs.status`/`started_at`.
- Review/Post‑Approval: `signals.*` (all 5 sub‑scores + `selected_as_hook` + `scope`), `drafts.body_sentences` (per‑sentence `type`/`signal_id` → inline citations + X/Y), `drafts.groundedness_pass`, `review_actions.action`/`reason`/`reviewed_at`, `audit_log`.
- Dashboard: existing `/api/metrics` + enriched run list.

No new tables/columns. (A denormalized groundedness count could be persisted for speed but is unnecessary at this scale and would touch stage code — explicitly avoided.)

## Backend — read‑side/data‑fetch changes only
1. **Enrich `GET /api/runs`** (`backend/app/api/runs.py:97`). For each row add, alongside existing fields: `title` (`prospect.title`), `persona_name` + `persona_assumed` (query `PersonaMapping` by run — same pattern as the existing `top_signal`/`latest_draft` lookups), `groundedness_pct` + `groundedness_grounded`/`groundedness_total` (derived helper, below), `personalization_depth` (helper), and for the Dashboard "Signal Detected" column `signal_type` + `signal_source_domain` (from `top_signal.type` and the host of `top_signal.source_url`). Optional `sort` query param (`newest|score|status`); client‑side sort is acceptable too. Wrap the item in a new `RunListItem` Pydantic schema in `schemas.py` (currently a raw dict).
2. **Shared read helpers** (new `backend/app/services/run_readmodel.py` or similar):
   - `personalization_depth(run, db)` — extract the inline logic now in `metrics.py:32‑43` (0 / 1 company / 2 individual) and reuse in both `metrics.py` and `runs.py` (refactor, no behavior change).
   - `groundedness_ratio(draft)` — parse `draft.body_sentences` JSON: `total` = sentences with `type == "fact"`, `grounded` = those with a `signal_id`; return `(grounded, total, pct)`. Fallback to `groundedness_pass` when `body_sentences` is empty.
3. **Optional: `GET /api/metrics` sub‑counts** (`backend/app/api/metrics.py`). Add raw counts to `MetricsResponse` to power card sub‑labels ("156 approvals", "47/50 verified"): `accepted_count`/`reviewed_count`, `groundedness_drafts_pass`/`groundedness_drafts_total`, `escalated_count`/`completed_count`. **No trend deltas.** All are simple reads over data already loaded in the endpoint.
4. **`GET /api/runs/{id}`**: no change needed — `DraftOut.body_sentences` and full `signals` are already returned, so the Review screen derives inline citations, the 5‑axis table, and the 3/3 ratio client‑side (or via helper #2 if surfaced).
5. Untouched: `POST /api/prospects`, `GET /api/fixtures`, `GET /api/runs/{id}/status`, `POST /api/runs/{id}/retry`, `PATCH /api/drafts/{id}/review`, and all of `pipeline/`, `llm/`, `services/scoring.py`, `persona_library.py`.

## Frontend — work per area (re‑skinned to `DESIGN.md`, light mode)
**Shared shell & tokens**
- New `frontend/css/tokens.css` — port every `DESIGN.md` token (colors, typography, spacing 8px grid, radii, component specs). Rewrite `frontend/css/style.css` against these (replace `--bg-dark`/`--blue`/etc.). Load Inter + JetBrains Mono.
- New `frontend/js/layout.js` — injects the fixed **Ink sidebar** (240px: brand "Z" + "Zamp AI SDR / ANALYTICAL RESEARCH", primary "New Research", section "Workspace" → Dashboard, Run List, with active state) and the 56px top bar (breadcrumb). Include on all pages (avoids duplicating markup across the 3 HTML files; no build step).

**`index.html` + `intake.js` (New Research)** — intake card: eyebrow "Prospect Intake", title "Research a new prospect", subtitle, fields Name / (Title + Company) / optional **Research source** dropdown (keep existing `fixture_id`, relabel; drop "Campaign"), "Start Research" primary button, 8‑stage pipeline hint strip. Same `createProspect` → redirect to `run.html?id=`.

**`run.html` + `run-view.js`** — single page, state‑driven (keep 1.5s polling of `/status`, full `/runs/{id}` on change):
- *Running* → Research Progress layout: status header (initials avatar, name, RUNNING badge, `title · company · persona`), "Execution Pipeline" (8 grouped rows w/ done✓/active/queued + elapsed from `audit_log`), active stage expands to persona (name + ASSUMED, goals/pains/KPIs) and Contextual Signals (from `signals`). Drop System Resources / persona % / Pause / fake logs.
- *Review* → two‑column co‑equal: **left** Generated Draft (subject input, body textarea with inline `S1/S2…` citation markers from `body_sentences.signal_id`, groundedness "N of N claims traced", buttons Reject / Approve with Edits / **Approve**); **right** Reasoning Trail — Web Research source cards (domain + URL + mono snippet), Hook Scoring 5‑axis table (REL/SPEC/REC/ACT/VER + HOOK, selected vs considered, score bars), Persona Match / Draft Generation / Groundedness Check collapsibles. Reuse existing review actions (`submitReview`).
- *Reviewed* → Post‑Approval: "Approval Confirmed" banner + decision record (`review_actions.action`/`reviewed_at`/`reason`), locked read‑only draft + Copy, archived reasoning trail. No "Sent via" / To‑From.
- *Insufficient / Needs‑research / Failed / Degraded* → status banner (warning/danger) + `escalation_reason` + degraded/halted stage markers from `audit_log`; **Retry** button on failed only.

**`dashboard.html` + `dashboard.js` (Performance Dashboard)** — 5 metric cards from `/api/metrics` (value + optional real sub‑count; no trend arrows) + "Recent Runs" mini‑table (Prospect·Company, Status badge, Signal Detected = hook `type` + source domain, Confidence = `top_hook_score`%) from `GET /api/runs?per_page=6`. Drop Campaign column.

**NEW `run-list.html` + `frontend/js/run-list.js` (Run List)** — full enriched table (Prospect, Title·Company, Persona +ASSUMED, Status badge, Groundedness bar+%+X/Y, Depth, Updated), header Search (client filter) / Filter (status) / Export (optional client‑side CSV), "N of M runs", sort, pagination — all from the enriched `GET /api/runs`. Move the heavy table here; Dashboard keeps only the mini "Recent Runs".

**`api.js`** — add `getRuns` enriched params (sort/search/status/page) and, if added, the metrics sub‑count fields; no breaking changes to existing callers.

## Files
- **Create:** `frontend/run-list.html`, `frontend/js/run-list.js`, `frontend/js/layout.js`, `frontend/css/tokens.css`, `backend/app/services/run_readmodel.py` (helpers).
- **Modify (frontend):** `index.html`, `run.html`, `dashboard.html`, `css/style.css`, `js/api.js`, `js/intake.js`, `js/run-view.js`, `js/dashboard.js`.
- **Modify (backend, read‑only):** `app/api/runs.py` (enrich list + `RunListItem`), `app/api/metrics.py` (optional sub‑counts + use helper), `app/models/schemas.py` (`RunListItem`, optional metrics fields).
- **Untouched:** everything in `app/pipeline/`, `app/llm/`, `app/services/scoring.py`, `app/services/persona_library.py`, `app/models/db_models.py` (no schema change), all stage logic.

## Phased implementation (when approved to build)
1. Tokens + shared shell (`tokens.css`, `layout.js`, rewrite `style.css`).
2. Backend list enrichment + read helpers.
3. Run List + Dashboard.
4. New Research.
5. `run.html` states (running / review / reviewed / degraded).

**Build-ready, per-stage guide:** [`docs/ui-stages/`](docs/ui-stages/) splits this into one
file per screen (with a shared-context preamble) so each can be handed to a fresh chat alongside
the screen's screenshot — see [`docs/ui-stages/README.md`](docs/ui-stages/README.md). There,
`run.html` is split into three stages (running / review / reviewed+error), so the 5 phases above
map to 8 stage files.

## Verification
- **Backend:** `cd backend && pytest tests/ -v` (existing tests must stay green — no core logic touched). Spot‑check `GET /api/runs` returns the new fields and `GET /api/metrics` still validates; confirm `groundedness_ratio` matches `body_sentences` on a known run.
- **Frontend:** serve `frontend/` (`python -m http.server 5500`) against a running backend (`uvicorn app.main:app --reload --port 8000`); walk a full run intake → live → review → approve, plus Run List filter/sort and Dashboard, in a ≤1024px and ≥1280px viewport. Confirm: Ink sidebar + Mist page + Inter/JetBrains Mono render; reasoning trail is co‑equal; snippets carry domain+URL; score bars show numeric value; no "Send"/Campaign/System‑Resources/trend‑arrow artifacts remain.
- **Cross‑check** rendered screens against the 6 Claude Design references (structure/labels), substituting `DESIGN.md` tokens.
