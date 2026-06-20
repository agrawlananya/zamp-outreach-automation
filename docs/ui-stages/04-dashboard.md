# Stage 4 — Performance Dashboard

> **Fresh chat?** Attach `00-shared-context.md` first, then this file.
> 📎 **Provide:** screenshot of the **Performance Dashboard**.
> **Depends on:** Stage 1, Stage 2.

**Goal:** Rework `dashboard.html` into 5 metric cards + a compact "Recent Runs" mini-table
(move the heavy table to Run List).

**Files:** modify `frontend/dashboard.html` + `frontend/js/dashboard.js`.

**Data:** `GET /api/metrics` for cards; `GET /api/runs?per_page=6` for recent runs.
**Cards (5):** Human Acceptance (`acceptance_rate`) · Groundedness (`groundedness_pct`) ·
Escalation Rate (`escalation_rate`) · Avg. Time-to-Draft (`avg_time_to_draft_ms`→`s`) ·
Personalization (`avg_personalization_depth`, "/2"). Each: `label-md` label, `display` value,
`body-sm` muted sub-count (real counts only, **no ↑/↓ arrows**).
**Recent Runs mini-table:** Prospect · Company · Status badge · Signal Detected
(`signal_type` · `signal_source_domain`) · Confidence (`top_hook_score`%). Row → `run.html?id=`.

**Screen-specific guardrails:** no trend arrows; no Campaign column; "Last 7 days" may appear
only as a static context label (not a working time filter unless backed).

**Done when:** five cards + mini-table render from live data, tokenized, no fabricated trends.
Commit: `feat(ui): performance dashboard (metric cards + recent runs)`.
