# Zamp AI SDR — UI Redesign: Staged Implementation

Build-ready, split from `UI_REDESIGN_PLAN.md`. Each stage is a separate file meant to be handed
to a **fresh Claude Code chat** in this repo, one at a time, with the screen's screenshot.

## How to use
For each stage:
1. Open a fresh Claude Code chat **in this repo**.
2. Attach (or paste) **`00-shared-context.md`** — the same preamble for every stage.
3. Attach (or paste) the **one stage file** you're building (e.g. `03-run-list.md`).
4. Attach the **screenshot** named at the top of that stage file.
5. Let it implement → verify → commit. New chat for the next stage.

> ⚠️ The screenshots are the *original* Claude Design mockups (IBM Plex / indigo / light+dark)
> and still contain features the product doesn't support. The shared context tells the chat to
> **reproduce the layout but re-skin to `DESIGN.md` tokens and apply the Guardrails** — never
> rebuild a dropped feature just because it's in the screenshot.

## Files
| File | Stage |
|---|---|
| `00-shared-context.md` | Preamble — attach with every stage |
| `01-tokens-and-shell.md` | Design tokens + shared sidebar/topbar shell |
| `02-backend-read-enrichment.md` | Backend read-side enrichment (no schema/pipeline changes) |
| `03-run-list.md` | Run List screen (new) |
| `04-dashboard.md` | Performance Dashboard |
| `05-new-research.md` | New Research (intake) |
| `06-run-running.md` | `run.html` — Running (Research Progress) |
| `07-run-review.md` | `run.html` — Review (Review Draft) |
| `08-run-terminal-states.md` | `run.html` — Post-Approval + degraded/failed |

## Order & dependencies
`01 → 02 → 03 → 04 → 05 → 06 → 07 → 08`
- **01** (tokens/shell) and **02** (backend) are prerequisites.
- **03** & **04** need **02** (enriched `GET /api/runs`).
- **05** needs **01**.
- **06 / 07 / 08** all edit `run.html` — build them in sequence.

Full rationale and the design source-of-truth live in `../../UI_REDESIGN_PLAN.md` and `../../DESIGN.md`.
