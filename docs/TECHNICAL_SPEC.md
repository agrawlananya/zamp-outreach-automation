# Technical Specification

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/prospects` | Create prospect + kick off a run. Returns `{run_id}`. |
| GET | `/api/runs` | Paginated run list. Query params: `status`, `date_from`, `date_to`, `page`, `per_page`. |
| GET | `/api/runs/{run_id}` | Full run detail: all stages, signals, persona, draft, audit trail. |
| GET | `/api/runs/{run_id}/status` | Lightweight poll: `{current_stage, percent_complete, status}`. |
| POST | `/api/runs/{run_id}/retry` | Re-run from last successful stage. Creates a new run record. |
| PATCH | `/api/drafts/{draft_id}/review` | Submit human decision: `approve`, `approve_with_edits`, or `reject`. |
| GET | `/api/metrics` | Aggregate North Star metrics for dashboard cards. |

---

## Pipeline — 11 Stages

The `PipelineOrchestrator` runs these in sequence. Each stage is a standalone function with typed Pydantic in/out. The orchestrator writes one `audit_log` row per stage.

```
Stage 1   intake_and_normalize(prospect)           → NormalizedProspect
Stage 2   research_prospect(name, company)         → (RawCorpus, RawCorpus)  # company + individual, capped at 12 URLs, scraped concurrently
Stage 4   extract_signals(corpora)                 → list[Signal]       # LLM: extractor, parallelized across pages
Stage 5   validate_signals(signals)                → list[Signal]       # LLM: verifier, parallelized across signals
Stage 6   map_persona(title)                       → Persona
Stage -   rank_candidate_signals(signals)          → top-K signals      # deterministic, no LLM call
Stage 7   map_pain(top_k_signals, persona)         → list[PainMapping]  # LLM: pain-mapping, parallelized across signals
Stage 8   score_and_select_hook(top_k_signals, pains) → HookSelection
Stage 9   generate_draft(hook, persona, pains)     → Draft              # LLM: writer
Stage 10  score_draft(draft, signals)              → RubricScore        # LLM: critic
Stage 11  route(rubric_score, hook_score)          → RunStatus          # deterministic
```

---

## LLM Roles — 4 Separate Prompts

All use Claude (Anthropic). The same model must not both generate and solely verify a claim.

| Role | Stage | Temp | Contract |
|---|---|---|---|
| **Extractor** | 4 | 0.1 | Emit a claim only if a verbatim `source_snippet` from the input text supports it. No inference beyond what is literally stated. Returns at most 3 signals per page, prioritizing the most recent/specific. |
| **Verifier** | 5 | 0.1 | Given `{claim, source_snippet}` (no prior context), return `valid / invalid / uncertain` + one-line reason. |
| **Writer** | 9 | 0.5 | Given `{hook, persona, pain_mappings, prospect_first_name, sender_name, sender_title}`. Returns `subject` + `subject_alt` (A/B options, lowercase, <42 chars) + a 70-110 word `body`: greeting (first name only) → 3 short paragraphs (hook / value+credibility / one-question CTA) → sign-off. No em/en dashes (enforced by prompt + a post-generation sanitizer in `stage9_draft_generation.py`). May not introduce any fact not present in the supplied signal set. Sender identity comes from `SENDER_NAME`/`SENDER_TITLE` settings (no per-user concept yet). |
| **Critic** | 10 | 0.1 | Score draft against rubric (relevance, specificity, personalization depth, credibility, clarity, brevity, groundedness). Return structured scores. Groundedness fail = automatic flag. |

---

## Hook Scoring Formula

```python
hook_score = (
    0.35 * relevance_to_owned_pain +
    0.25 * specificity +
    0.20 * recency +
    0.10 * actionability +
    0.10 * verifiability_confidence
)
# Each sub-score in [0.0, 1.0]
# Gate: hook_score < 0.45 → route to insufficient_signal
```

Before pain-mapping, validated signals are pre-ranked by `stage8_hook_scoring.rank_candidate_signals` on the four sub-scores that don't depend on pain-mapping (specificity, recency, actionability, verifiability — no LLM call involved). Only the top 8 go on to pain-mapping and hook-scoring; this avoids spending a pain-mapping LLM call on a signal that has no realistic chance of being selected as the hook. Stage 10's groundedness check still sees every validated signal, not just the top 8.

All sub-scores for all candidate signals are stored and surfaced in the UI — not just the winner.

---

## Run Status State Machine

```
pending → running → ready_for_review       (hook ≥ 0.45 AND groundedness pass)
                  → insufficient_signal    (hook < 0.45)
                  → needs_human_research   (groundedness fail after 1 regeneration)
                  → deprioritized          (non-ICP)
                  → failed                 (unrecoverable after retries)
         → reviewed  (terminal — set when review_action is recorded)
```

---

## Database Schema (SQLite / SQLAlchemy)

```sql
-- prospects
id TEXT PK, name TEXT, title TEXT, company_name TEXT,
company_domain TEXT, linkedin_url TEXT, created_at TIMESTAMP

-- runs
id TEXT PK, prospect_id TEXT FK, status TEXT, current_stage TEXT,
started_at TIMESTAMP, completed_at TIMESTAMP,
time_to_draft_ms INTEGER, escalation_reason TEXT

-- signals
id TEXT PK, run_id TEXT FK, scope TEXT (company|individual),
type TEXT, claim TEXT, source_url TEXT, source_snippet TEXT,
signal_date DATE, entity TEXT, validated BOOLEAN, validation_reason TEXT,
relevance_score REAL, specificity_score REAL, recency_score REAL,
actionability_score REAL, verifiability_score REAL,
hook_score REAL, selected_as_hook BOOLEAN

-- persona_mappings
id TEXT PK, run_id TEXT FK, persona_name TEXT, is_assumed BOOLEAN,
goals TEXT (JSON), pains TEXT (JSON), kpis TEXT (JSON)

-- pain_mappings
id TEXT PK, run_id TEXT FK, signal_id TEXT FK,
owned_pain TEXT, owned_kpi TEXT, zamp_value_prop TEXT

-- drafts
id TEXT PK, run_id TEXT FK, version INTEGER,
subject TEXT, subject_alt TEXT, body TEXT, sources_used TEXT (JSON array of signal ids),
rubric_scores TEXT (JSON), groundedness_pass BOOLEAN, created_at TIMESTAMP

-- review_actions
id TEXT PK, draft_id TEXT FK,
action TEXT (approve|approve_with_edits|reject),
edited_body TEXT, reason TEXT, reviewed_at TIMESTAMP

-- audit_log  (append-only — never update or delete)
id TEXT PK, run_id TEXT FK, stage TEXT,
input_snapshot TEXT (JSON), output_snapshot TEXT (JSON),
model_used TEXT, latency_ms INTEGER,
status TEXT (ok|degraded|failed), error_message TEXT, created_at TIMESTAMP
```

---

## Error Handling Rules

1. Wrap every external call (Tavily, scrape, LLM) in try/except with retry + exponential backoff.
   - Default: 3 attempts, delays 1s → 2s → 4s.
2. On exhausted retries: write `status='degraded'` to `audit_log`, continue the pipeline with partial data.
3. If partial data makes the pipeline unrunnable: write `status='failed'`, set `runs.status='failed'`.
4. Never raise unhandled exceptions to the API layer — catch and return a structured error response.
5. One regeneration cap on drafts. If critic flags groundedness fail: regenerate once → if still failing, set `needs_human_research`.

---

## Required Edge Cases

**EC-1 — No public data (stealth company)**
- Detect: research corpus below minimum size after stages 2–3.
- Route to `insufficient_signal`. Show honest non-personalized fallback. Never disguise it as personalized.

**EC-2 — Multiple strong signals (≥ 2 signals score > 0.6)**
- Pick exactly one hook. Do not blend signals into one email.
- Store all runner-up scores in the signal table. Surface them in the UI as "considered, not selected."

**EC-3 — Prospect changed companies recently**
- Detect: individual signal of type `role_change` with date newer than submitted company.
- Re-anchor company research to new company. Flag transition explicitly in audit trail.
- If ambiguous → `needs_human_research`.

**EC-4 — Tool failure mid-run**
- Covered by baseline retry/backoff. If still failing after retries, continue pipeline with existing data.
- Thinner signal set → lower hook score → may naturally trigger `insufficient_signal`. That is the correct behavior.

---

## Frontend Pages (Plain HTML/CSS/JS)

| File | Route | Purpose |
|---|---|---|
| `index.html` | `/` | Intake form: Name, Title, Company. POST to `/api/prospects`, redirect to run.html?id=... |
| `run.html` | `/run.html?id=...` | Live Run View (polling) → auto-switches to Review once `status != running`. |
| `dashboard.html` | `/dashboard.html` | Metric cards + run history table. |

### Run View polling
- Poll `GET /api/runs/{id}/status` every 1500ms while `status === 'running'`.
- Once status changes, fetch full run detail (`GET /api/runs/{id}`) and render the review panel.
- Do not poll after a terminal status is reached.

### Review screen actions
- **Approve** → `PATCH /api/drafts/{draft_id}/review` with `{action: "approve"}`
- **Approve with edits** → same with `{action: "approve_with_edits", edited_body: "..."}` 
- **Reject** → same with `{action: "reject", reason: "..."}`

---

## Signal Types (reference)

Common values for `signals.type`:
`new_cfo`, `new_general_counsel`, `new_cmo`, `new_ciso`, `new_controller`, `role_change`, `funding_round`, `acquisition`, `ipo_prep`, `hiring_finance`, `audit_finding`, `system_migration`, `regulatory_change`, `leadership_change`, `earnings_call_mention`

This list is not exhaustive — the extractor LLM determines type from source content, across any function (not just finance).

Hook-scoring actionability (stage 8) is pattern-based, not a finance-only allowlist: any type prefixed `new_` or suffixed `_migration`, plus a fixed set of cross-functional event categories (`role_change`, `leadership_change`, `funding_round`, `acquisition`, `ipo_prep`, `merger`, `reorg`, `regulatory_change`, `system_migration`), scores actionability 1.0. See `app/pipeline/stage8_hook_scoring.py`.

---

## Persona Library (Static Config)

Loaded from `services/persona_library.py`. A dict keyed by lowercase title alias (70+ aliases), organized into ~14 functional sections (Exec/Board, Finance & Accounting, Procurement, Compliance & Risk, Legal, Marketing, Sales, IT & Technology, Cybersecurity, Product & Engineering, RevOps & GTM, Customer Success & Support, Recruiting & People Ops, Data Operations, Operations). Each persona has: `name`, `buyer_type` (`economic` | `functional` | `manager`, per Miller Heiman), `goals[]`, `pains[]`, `kpis[]`, `messaging_angle`, `zamp_value_prop`.

Stage 6 does an exact title lookup first. If no match, uses the LLM to pick the nearest persona and sets `is_assumed=True` on the `persona_mappings` record.
