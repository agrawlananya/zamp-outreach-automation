# Stage 2 — Backend read-side enrichment (data the UI needs)

> **Fresh chat?** Attach `00-shared-context.md` first, then this file.
> 📎 **Provide:** none (backend-only).
> **Depends on:** none (do before Run List + Dashboard).

**Goal:** Expose the extra read-only fields the new screens need — **no schema or pipeline
changes**.

**Files:**
- Create `backend/app/services/run_readmodel.py`:
  - `personalization_depth(run, db) -> int` — move the inline logic from `metrics.py` (≈ lines
    32–43): 0 if no `selected_as_hook` signal; 2 if that signal `scope=="individual"`; else 1.
  - `groundedness_ratio(draft) -> (grounded:int, total:int, pct:int)` — parse
    `draft.body_sentences` JSON: `total` = sentences with `type=="fact"`; `grounded` = those
    with a truthy `signal_id`; `pct = round(100*grounded/total)` (0 if total 0). Fallback to
    `groundedness_pass` (→ 1/1 or 0/1) when `body_sentences` is empty.
- Modify `backend/app/api/runs.py` (`list_runs`, ≈ line 97): for each row also return `title`,
  `persona_name`, `persona_assumed` (one `PersonaMapping` query per run, mirroring the existing
  `top_signal`/`latest_draft` lookups), `groundedness_pct`/`groundedness_grounded`/
  `groundedness_total` (from `groundedness_ratio` on the latest draft), `personalization_depth`,
  and `signal_type`/`signal_source_domain` (from the hook signal's `type` and the host parsed
  from `source_url`). Add an optional `sort` query param (`newest|score|status`, default
  `newest`). Wrap each item in a new `RunListItem` schema.
- Modify `backend/app/models/schemas.py`: add `RunListItem`; optionally extend `MetricsResponse`
  with sub-counts (`accepted_count`,`reviewed_count`,`groundedness_drafts_pass`,
  `groundedness_drafts_total`,`escalated_count`,`completed_count`).
- Modify `backend/app/api/metrics.py`: import + use `personalization_depth` (remove the dupe);
  if you added sub-counts, populate them from data already queried. **No trend deltas.**

**Screen-specific guardrails:** read-only joins/derivations only; do not touch stage code or
add columns; `metrics.py` numeric outputs must not change.

**Done when:** `pytest tests/ -v` stays green; `GET /api/runs` returns the new fields and
`GET /api/metrics` still validates; `groundedness_ratio` matches `body_sentences` on a known
run. Commit: `feat(api): enrich GET /api/runs read model (+ shared read helpers)`.
