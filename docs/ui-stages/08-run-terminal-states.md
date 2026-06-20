# Stage 8 — run.html: Reviewed (Post-Approval) + error/degraded states

> **Fresh chat?** Attach `00-shared-context.md` first, then this file.
> 📎 **Provide:** screenshot of the **Post-Approval** screen (and the degraded/insufficient/failed shot if you have one).
> **Depends on:** Stage 1, Stage 7.

**Goal:** Terminal states for `run.html`.

**Files:** modify `frontend/run.html` + `frontend/js/run-view.js`.

**Reviewed (Post-Approval):** success-subtle banner "Approval Confirmed" + decision record from
`review_actions` (action, `reviewed_at`, optional reason) + **Copy draft** button. Locked,
read-only draft (mono body), "Recipient: {name} · {title}, {company}" (no emails). Archived
reasoning trail (same trust content, read-only).
**Insufficient / Needs research / Failed / Degraded:** status banner (warning for
insufficient/needs-research, danger for failed) + `escalation_reason`; pipeline shows the
degraded/halted stage (▲) from `audit_log`; **Retry** button **only** when `status==="failed"`
(calls `retryRun`, then navigates to the new run). Insufficient signal shows the honest
fallback, never a fabricated draft.

**Screen-specific guardrails:** **drop** "Sent via Outreach.io", To/From, Override Threshold,
Mark as Dead. Recovery = Retry only.

**Done when:** every terminal status renders its correct state; reviewed shows the decision +
Copy; failed offers Retry; insufficient shows fallback. Commit:
`feat(ui): post-approval + degraded/failed run states`.

---

## Appendix — verification (run after any stage)
- Backend touched → `cd backend && pytest tests/ -v` (must stay green).
- Manual walk: backend on `:8000`, `python -m http.server 5500` in `frontend/`, then
  intake → live run → review → approve; plus Run List filter/sort and Dashboard. Test at
  ≤1024px and ≥1280px widths.
- Confirm: Ink sidebar + Mist page + Inter/JetBrains Mono; reasoning trail co-equal; snippets
  carry domain+URL; score bars show numbers; **no** Send / Campaign / System-Resources /
  trend-arrow / To-From artifacts remain.
- Cross-check the rendered screen against the provided screenshot (structure + labels), with
  `DESIGN.md` tokens substituted for the mockup's colors/fonts.
