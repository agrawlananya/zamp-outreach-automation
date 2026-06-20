# Stage 1 — Design tokens + shared app shell

> **Fresh chat?** Attach `00-shared-context.md` first, then this file.
> 📎 **Provide:** a screenshot showing the **sidebar + top bar** (any screen; New Research or Run List is ideal).
> **Depends on:** none. **Do first.**

**Goal:** Establish the token layer and a reusable shell (Ink sidebar + top bar) used by all
pages, without breaking current functionality.

**Files:**
- Create `frontend/css/tokens.css` (the `:root` block from Shared Context).
- Create `frontend/js/layout.js` — renders the shell into a mount point and marks the active nav.
- Modify `frontend/css/style.css` — rewrite against the token vars; delete ad-hoc vars
  (`--bg-dark`, `--blue`, …). Define component classes: `.sidebar`, `.topbar`, `.app-shell`,
  `.card`, `.btn`/`.btn--primary|secondary|success|danger`, `.badge`/`.badge--*`,
  `.score-bar`, `.snippet`, `.stage-row`, `.metric-card`, `.data-table`.
- Modify `index.html`, `run.html`, `dashboard.html` — add Google Fonts `<link>` (Inter +
  JetBrains Mono) + `tokens.css`, replace the old `<header class="app-header">` with the shell
  (call `layout.js`).

**Implementation notes:**
- Sidebar (240px, `--sidebar-bg`, fixed left): brand "Z" mark + "Zamp AI SDR" +
  "ANALYTICAL RESEARCH" eyebrow; primary **New Research** action; "WORKSPACE" label; nav items
  **Dashboard**, **Run List**. Active item uses `--sidebar-active-bg` + `--sidebar-text-active`
  + `headline-sm`. Collapses to icon-only (~48px) below 1024px (nice-to-have).
- Top bar (56px, paper, 1px bottom border): page title (per `DESIGN.md` "page title only").
- `layout.js` API: `renderLayout({ active: 'new-research'|'dashboard'|'runs', title })`,
  mounted into a `<div id="app-shell">`. Keep it dependency-free; no build step.

**Screen-specific guardrails:** sidebar has exactly 3 destinations (no Prospects/Campaigns/Settings).

**Done when:** all three existing pages render inside the new shell with Mist page bg, Ink
sidebar, Inter/JetBrains Mono, correct active nav; existing intake/run/dashboard behavior is
unchanged. Commit: `feat(ui): design tokens + shared sidebar/topbar shell`.
