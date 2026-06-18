# Development Stages — Zamp AI SDR MVP

No unit tests. Build each stage end-to-end before moving to the next. Verify by running manually.

---

## Stage 0 — Project Scaffold
**Goal:** A running skeleton. No pipeline logic yet — just the project structure, DB, and a health check endpoint you can `curl`.

**Claude Code instructions:**

> Create the full project folder structure as defined in CLAUDE.md. Then:
>
> 1. Create `backend/requirements.txt` with: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `pydantic-settings`, `anthropic`, `tavily-python`, `requests`, `beautifulsoup4`, `python-dotenv`, `aiofiles`
> 2. Create `backend/.env.example` with all four env vars from CLAUDE.md (empty values)
> 3. Create `backend/app/core/config.py` — load env vars using `pydantic-settings`. Fields: `LLM_API_KEY`, `LLM_PROVIDER`, `TAVILY_API_KEY`, `DATABASE_URL`, `CORS_ALLOWED_ORIGIN`
> 4. Create `backend/app/db/database.py` — SQLAlchemy engine + `SessionLocal` + `get_db` dependency
> 5. Create `backend/app/models/db_models.py` — all 7 SQLAlchemy ORM models from the schema in TECHNICAL_SPEC.md
> 6. Create `backend/app/db/init_db.py` — `create_all()` against the engine, runnable as `python -m app.db.init_db`
> 7. Create `backend/app/main.py` — FastAPI app with CORS middleware (origin from config), and a single `GET /health` endpoint returning `{"status": "ok"}`
> 8. Create `backend/app/models/schemas.py` — Pydantic schemas for all request/response shapes: `ProspectCreate`, `RunStatusResponse`, `RunDetailResponse`, `ReviewRequest`, `MetricsResponse`. Mirror the DB model fields.

**Done when:** `uvicorn app.main:app --reload --port 8000` starts, `curl localhost:8000/health` returns `{"status": "ok"}`, and `python -m app.db.init_db` creates the SQLite file with all 7 tables.

---

## Stage 1 — LLM Client + Prompt Modules
**Goal:** A working LLM wrapper and all 4 prompt functions, callable in isolation.

**Claude Code instructions:**

> 1. Create `backend/app/llm/client.py` — thin wrapper around the Anthropic SDK. Single function: `call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 2000) -> str`. Implement retry with exponential backoff (3 attempts, 1s/2s/4s). Raise a custom `LLMError` after exhausted retries.
>
> 2. Create `backend/app/llm/prompts/extractor.py` — function `build_extractor_prompt(raw_text: str, source_url: str) -> tuple[str, str]` returning `(system_prompt, user_prompt)`. The system prompt must instruct the model to: only emit a signal if a verbatim snippet from the provided text supports it; return a JSON array of objects with fields `{type, claim, source_snippet, signal_date, entity, scope}`; never infer beyond what is literally stated.
>
> 3. Create `backend/app/llm/prompts/verifier.py` — function `build_verifier_prompt(claim: str, source_snippet: str) -> tuple[str, str]`. System prompt: given only the claim and snippet (no other context), return JSON `{verdict: "valid"|"invalid"|"uncertain", reason: str}`.
>
> 4. Create `backend/app/llm/prompts/writer.py` — function `build_writer_prompt(hook_signal: dict, persona: dict, pain_mappings: list[dict]) -> tuple[str, str]`. System prompt: write a subject line and 60–90 word email body using only the supplied signals; no invented facts; follow structure: hook → bridge → pain/WIIFT → credibility → CTA. Return JSON `{subject: str, body: str}`.
>
> 5. Create `backend/app/llm/prompts/critic.py` — function `build_critic_prompt(subject: str, body: str, validated_signals: list[dict]) -> tuple[str, str]`. System prompt: score the draft on relevance, specificity, personalization_depth, credibility, clarity, brevity (each 1–5), plus `groundedness_pass: bool` (true only if every factual claim maps to a supplied signal). Return JSON.

**Done when:** You can open a Python shell, import `call_llm`, pass it a prompt, and get a string response back.

---

## Stage 2 — External Services
**Goal:** Search and scrape working with retry/backoff, returning clean structured data.

**Claude Code instructions:**

> 1. Create `backend/app/services/search_service.py`. Function: `search(query: str, max_results: int = 5) -> list[dict]`. Use the Tavily Python client. Each result dict must have: `url`, `title`, `content`, `published_date`. Wrap with retry/backoff (3 attempts, 1s/2s/4s). On exhausted retries, return an empty list and log the error — never raise.
>
> 2. Create `backend/app/services/scrape_service.py`. Function: `scrape(url: str) -> dict`. Use `requests` + `BeautifulSoup`. Extract: `url`, `title`, `body_text` (cleaned, no scripts/styles). Max body_text length: 8000 chars (truncate). Same retry/backoff pattern. On failure return `{url, title: "", body_text: "", error: str}`.
>
> 3. Create `backend/app/services/persona_library.py`. Hard-code the 5 finance personas as a Python dict (keyed by lowercase title). Each persona has: `name`, `goals: list[str]`, `pains: list[str]`, `kpis: list[str]`, `messaging_angle: str`, `zamp_value_prop: str`. Personas: `CFO`, `Controller`, `VP Finance`, `Head of Accounting`, `Finance/AP Ops Lead`. Use BUSINESS_CONTEXT.md as the source for pain/KPI content.
>    Add function `lookup_persona(title: str) -> tuple[dict, bool]` — returns `(persona, is_assumed)`. Exact match first (case-insensitive). If no match, call the LLM with a simple prompt to pick the nearest of the 5. `is_assumed=True` if LLM fallback was used.
>
> 4. Create `backend/app/services/scoring.py`. Function: `compute_hook_score(relevance, specificity, recency, actionability, verifiability) -> float`. Implement the exact formula from TECHNICAL_SPEC.md. Add helper `score_is_sufficient(hook_score: float) -> bool` (threshold 0.45).

**Done when:** You can manually call `search("CFO hiring fintech 2024")` and get a list back. You can call `lookup_persona("Chief Financial Officer")` and get the CFO persona.

---

## Stage 3 — Pipeline Stages 1–5 (Research + Signal Extraction)
**Goal:** Given a prospect input, produce a list of validated, sourced signals persisted to the DB.

**Claude Code instructions:**

> For each stage, create the file in `backend/app/pipeline/`. Each stage function takes Pydantic models as input and returns Pydantic models. Add any needed schemas to `schemas.py`. The orchestrator will call these — stages must not call each other.
>
> **stage1_intake.py** — `intake_and_normalize(prospect_id: str, db) -> NormalizedProspect`
> - Load prospect from DB. Resolve company domain: use a simple heuristic (lowercase company name, strip spaces, add .com) as the V1 approach — flag it in a comment as "good enough for MVP."
> - Update `prospects.company_domain` in DB. Return `NormalizedProspect {id, name, title, company_name, company_domain}`.
>
> **stage2_company_research.py** — `research_company(domain: str, company_name: str) -> RawCorpus`
> - Run 3 Tavily searches: `"{company_name} news"`, `"{company_name} CFO OR finance OR funding"`, `"{company_name} hiring OR layoffs OR expansion"`.
> - For each search result, call `scrape_service.scrape(url)`. Deduplicate by URL.
> - Return `RawCorpus {source: "company", items: list[{url, title, body_text, published_date}]}`.
>
> **stage3_individual_research.py** — `research_individual(name: str, company_name: str) -> RawCorpus`
> - Run 2 Tavily searches: `"{name} {company_name}"`, `"{name} CFO OR Controller OR finance"`.
> - Scrape results. Check each result: if the prospect's name does not appear in the `body_text`, discard it (identity verification).
> - Return `RawCorpus {source: "individual", items: [...]}`.
>
> **stage4_extract_signals.py** — `extract_signals(corpora: list[RawCorpus], run_id: str, db) -> list[Signal]`
> - For each corpus item with non-empty `body_text`, call `build_extractor_prompt` + `call_llm`. Parse the JSON response.
> - For each extracted signal, create a `Signal` DB record (validated=False, scores all null). 
> - Return the list of Signal objects.
>
> **stage5_validate_signals.py** — `validate_signals(signals: list[Signal], run_id: str, db) -> list[Signal]`
> - For each signal, call `build_verifier_prompt` + `call_llm`. Parse verdict.
> - Update signal DB record: `validated=True/False`, `validation_reason=reason`.
> - Return only signals where `validated=True`.

**Done when:** You can run stage 1–5 manually in a Python script with a real prospect and see validated signals in the SQLite DB.

---

## Stage 4 — Pipeline Stages 6–8 (Persona, Pain, Hook Scoring)
**Goal:** Map signals to a persona and pain, score all hooks, select the best one.

**Claude Code instructions:**

> **stage6_persona_mapping.py** — `map_persona(title: str, run_id: str, db) -> PersonaMapping`
> - Call `persona_library.lookup_persona(title)`. 
> - Create a `PersonaMapping` DB record (JSON-encode goals/pains/kpis).
> - Return the PersonaMapping.
>
> **stage7_pain_mapping.py** — `map_pain(signals: list[Signal], persona: PersonaMapping, run_id: str, db) -> list[PainMapping]`
> - For each validated signal, use a simple LLM call: given the signal's claim and the persona's pains list, which single pain does this signal most relate to? Return `{owned_pain, owned_kpi, zamp_value_prop}`.
> - Create `PainMapping` DB records. Return the list.
>
> **stage8_hook_scoring.py** — `score_and_select_hook(signals: list[Signal], pain_mappings: list[PainMapping], run_id: str, db) -> HookSelection`
> - For each signal, compute sub-scores using heuristics:
>   - `relevance`: 1.0 if signal has a matching pain_mapping, 0.3 otherwise
>   - `specificity`: 1.0 if signal has a named entity + specific claim, 0.5 if generic
>   - `recency`: 1.0 if signal_date within 90 days, 0.7 within 180 days, 0.3 within 365 days, 0.1 older
>   - `actionability`: 1.0 if type is in `[new_cfo, new_controller, role_change, funding_round, erp_migration]`, 0.5 otherwise
>   - `verifiability`: 1.0 if source_snippet is >50 chars, 0.5 if shorter
> - Compute `hook_score` using `scoring.compute_hook_score()`. Update each signal's score fields in DB.
> - Mark the highest-scoring signal as `selected_as_hook=True`.
> - Return `HookSelection {selected_signal, all_scores: list[{signal_id, hook_score, sub_scores}], top_score_sufficient: bool}`.

**Done when:** After running stages 1–8 on a real prospect, you can query the DB and see scores on every signal and exactly one with `selected_as_hook=True`.

---

## Stage 5 — Pipeline Stages 9–11 (Draft, Quality, Routing)
**Goal:** Generate a draft, score it, route the run to a final status.

**Claude Code instructions:**

> **stage9_draft_generation.py** — `generate_draft(hook: Signal, persona: PersonaMapping, pain_mappings: list[PainMapping], run_id: str, db) -> Draft`
> - Call `build_writer_prompt` + `call_llm` (temp 0.5). Parse JSON response for `{subject, body}`.
> - Create a `Draft` DB record (version=1, groundedness_pass defaults to False until stage 10 sets it).
> - Return the Draft.
>
> **stage10_quality_scoring.py** — `score_draft(draft: Draft, validated_signals: list[Signal], run_id: str, db) -> RubricScore`
> - Call `build_critic_prompt` + `call_llm`. Parse JSON scores.
> - Update `draft.rubric_scores` (JSON) and `draft.groundedness_pass` in DB.
> - Return `RubricScore {scores: dict, groundedness_pass: bool}`.
>
> **stage11_routing.py** — `route(hook_selection: HookSelection, rubric_score: RubricScore) -> str`
> - Pure deterministic function, no DB calls:
>   ```python
>   if not hook_selection.top_score_sufficient:
>       return "insufficient_signal"
>   if not rubric_score.groundedness_pass:
>       return "needs_human_research"
>   return "ready_for_review"
>   ```
> - Return the status string.
>
> **orchestrator.py** — `PipelineOrchestrator` class with a single `run(run_id: str, db)` method.
> - Execute stages 1–11 in order. After each stage, write one `audit_log` row: `{run_id, stage, input_snapshot (JSON), output_snapshot (JSON), model_used, latency_ms, status}`.
> - Update `runs.current_stage` after each stage completes.
> - If stage 10 returns `groundedness_pass=False`: regenerate once (call stage 9 again with `version=2`), re-run stage 10. If still failing, set status to `needs_human_research` without a second retry.
> - On any stage exception: log `status='degraded'`, continue if possible, or set `runs.status='failed'` and stop.
> - On completion, set `runs.status`, `runs.completed_at`, `runs.time_to_draft_ms`.

**Done when:** You can call `PipelineOrchestrator().run(run_id, db)` on a real prospect and see a completed run with a draft in the DB, and all audit_log rows written.

---

## Stage 6 — API Layer
**Goal:** All 7 endpoints working, pipeline triggered via BackgroundTasks, polling endpoint returning live stage updates.

**Claude Code instructions:**

> Wire up all API routes. Register all routers in `main.py`.
>
> **`api/prospects.py`** — `POST /api/prospects`
> - Accept `ProspectCreate {name, title, company_name}`. Validate server-side.
> - Create `Prospect` + `Run` (status=`pending`) DB records.
> - Enqueue `PipelineOrchestrator().run(run_id, db)` via `BackgroundTasks`.
> - Return `{run_id}` immediately.
>
> **`api/runs.py`**
> - `GET /api/runs/{run_id}` — return full run detail: run record + all signals + persona_mapping + pain_mappings + latest draft + all audit_log rows. Use a response schema that nests these.
> - `GET /api/runs/{run_id}/status` — return `{status, current_stage, percent_complete}`. Compute percent from a fixed map of stage names to percentages (stage1=9%, stage2=18%, … stage11=100%).
> - `GET /api/runs` — paginated list. Each row: `{id, prospect_name, company, status, top_hook_score, time_to_draft_ms, human_decision, created_at}`. Support `?status=`, `?page=`, `?per_page=` query params.
> - `POST /api/runs/{run_id}/retry` — only if `runs.status='failed'`. Create a new Run record for the same prospect, enqueue via BackgroundTasks. Return `{new_run_id}`.
>
> **`api/drafts.py`** — `PATCH /api/drafts/{draft_id}/review`
> - Accept `ReviewRequest {action, edited_body?, reason?}`.
> - Validate: action must be one of `approve`, `approve_with_edits`, `reject`.
> - Create `ReviewAction` DB record (never update an existing one).
> - Update `runs.status = 'reviewed'`.
> - Return `{ok: true}`.
>
> **`api/metrics.py`** — `GET /api/metrics`
> - Query the DB to compute:
>   - `acceptance_rate`: reviewed runs where action != 'reject' / total reviewed runs
>   - `groundedness_pct`: avg of drafts.groundedness_pass (as 0/1)
>   - `escalation_rate`: runs with status in ['insufficient_signal', 'needs_human_research'] / total completed runs
>   - `avg_time_to_draft_ms`: avg of runs.time_to_draft_ms
>   - `avg_personalization_depth`: avg of (2 if any individual signal selected, 1 if company signal, 0 if fallback)
> - Return as `MetricsResponse`.

**Done when:** You can `POST /api/prospects`, watch `GET /api/runs/{id}/status` update as the pipeline runs, and `GET /api/runs/{id}` shows the full completed run with draft.

---

## Stage 7 — Frontend
**Goal:** All 3 HTML pages working against the live backend. No frameworks, no build step.

**Claude Code instructions:**

> Create `frontend/css/style.css` — clean, minimal styles. Dark-ish sidebar/header, white content area. No animations. Legible font (system-ui or Inter from Google Fonts). Status badges use color (green=ready, yellow=needs_research, red=failed, grey=pending).
>
> Create `frontend/js/api.js` — a thin wrapper module. Export async functions mirroring each API endpoint: `createProspect(data)`, `getRunStatus(runId)`, `getRunDetail(runId)`, `getRuns(params)`, `submitReview(draftId, data)`, `getMetrics()`. All use `fetch()` pointed at `http://localhost:8000`. Export a shared `API_BASE_URL` constant at the top.
>
> **`frontend/index.html` + `frontend/js/intake.js`**
> - Single form: Name (text), Title (text), Company (text). All required.
> - On submit: disable button, call `createProspect()`, on success redirect to `run.html?id={run_id}`.
> - On error: show inline error message (never alert()).
>
> **`frontend/run.html` + `frontend/js/run-view.js`**
> - On load, read `?id=` from URL. If missing, redirect to `/`.
> - **Live phase** (status === 'running' or 'pending'):
>   - Poll `getRunStatus(runId)` every 1500ms.
>   - Render a vertical stage list (11 stages). Each stage shows: pending (grey dot) / running (spinner) / done (checkmark) / degraded (warning icon). Show `current_stage` as active.
>   - Stop polling once status is no longer 'running'/'pending'.
>   - Fetch full run detail and switch to review phase.
> - **Review phase** (any terminal status):
>   - Two-column layout. Left: editable draft (subject input + body textarea). Right: reasoning trail panel.
>   - Reasoning trail shows: chosen hook + score, all candidate signals with sub-scores table, persona name (flagged if assumed), matched pain, sources list (each with URL + snippet).
>   - Status banners:
>     - `insufficient_signal`: yellow banner "Low confidence — fallback draft. Manual research recommended."
>     - `needs_human_research`: orange banner "Groundedness check failed. Review carefully before sending."
>     - `failed`: red banner "Run failed — [escalation_reason]. Use retry button."
>   - Three action buttons: **Approve**, **Approve with Edits**, **Reject**.
>     - Approve: calls `submitReview(draftId, {action: "approve"})`.
>     - Approve with edits: calls with `{action: "approve_with_edits", edited_body: textarea.value}`.
>     - Reject: shows a small reason input inline, then calls with `{action: "reject", reason}`.
>   - After any action: disable buttons, show "Decision recorded" confirmation.
>
> **`frontend/dashboard.html` + `frontend/js/dashboard.js`**
> - On load, call `getMetrics()` and `getRuns({page: 1, per_page: 20})` in parallel.
> - Render 5 metric cards at top: Acceptance Rate, Groundedness %, Escalation Rate, Avg Time-to-Draft, Avg Personalization Depth.
> - Render a sortable table below: columns are Prospect, Company, Status, Hook Score, Time-to-Draft, Decision, Date.
> - Each row is clickable — navigate to `run.html?id={run_id}` (read-only, actions already disabled if status=reviewed).
> - Add simple status filter dropdown above the table (All / Ready / Insufficient / Failed / Reviewed).

**Done when:** Full happy-path flow works in the browser: fill form → watch live run view update → see draft + reasoning trail → click Approve → status updates → appears in dashboard.

---

## Stage 8 — Edge Cases + Hardening
**Goal:** The 4 required edge cases behave correctly. The system degrades gracefully under failure.

**Claude Code instructions:**

> Handle these in the existing pipeline stage files — no new files needed.
>
> **EC-1 (no public data):** In `stage2_company_research.py`, after scraping, count total non-empty `body_text` items. If fewer than 2, set a flag on the `RawCorpus`: `{..., thin_corpus: True}`. In `stage8_hook_scoring.py`, if both company and individual corpora were thin, force all signal scores to 0.1 max, which will naturally produce `hook_score < 0.45` → `insufficient_signal`.
>
> **EC-2 (multiple strong signals):** Already handled by architecture — stage 8 selects exactly one hook and stores all others. Verify in run.html that the reasoning trail renders the runner-up signals with label "Considered — not selected."
>
> **EC-3 (prospect changed companies):** In `stage3_individual_research.py`, after scraping, scan extracted text for patterns like "joins", "appointed at", "moves to" combined with a company name different from the submitted one. If found, add a special signal of type `role_change` to the corpus metadata and log a note in the audit_log. In `stage1_intake.py`, if a `role_change` signal with a newer date is detected during stage 3 re-entry, update `runs.escalation_reason` with a note and set status to `needs_human_research`.
>
> **EC-4 (tool failure):** Already handled by the retry/backoff wrappers. Verify: simulate a failure by temporarily passing an invalid Tavily key, confirm the pipeline completes with `status='degraded'` on the research stages and routes to `insufficient_signal` (not a crash).
>
> **Final hardening pass:**
> - Review every external call site. Confirm retry wrappers are in place.
> - Confirm no raw exception tracebacks can reach the frontend (check all API routes have top-level try/except).
> - Confirm `audit_log` rows are written for every stage, including failed ones.
> - Confirm the one-regeneration cap is enforced in the orchestrator.
> - Manually run 3 real prospects end-to-end. Fix anything that breaks.

**Done when:** All 4 edge cases produce the correct UI state. Three real prospects run start-to-finish without manual intervention.

---

## Completion Checklist

Before calling the MVP done, verify each of these manually:

- [ ] New prospect form submits and redirects to live run view
- [ ] Live run view stages update in real time as pipeline progresses
- [ ] Completed run shows draft + full reasoning trail (signals, scores, sources)
- [ ] Approve / Approve with edits / Reject all work and persist correctly
- [ ] `insufficient_signal` run shows yellow banner + generic fallback draft (not a fake-personal one)
- [ ] Dashboard shows correct metric cards and run history
- [ ] Dashboard row click opens the run detail in read-only mode
- [ ] A simulated tool failure degrades gracefully — no crash, no blank screen
- [ ] All API keys are in `.env` and never appear in any `.js` file
- [ ] `audit_log` has a row for every stage of every run
