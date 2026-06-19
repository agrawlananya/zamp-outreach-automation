# Zamp AI SDR — Claude Code Constitution

## What This Project Is
An internal AI tool that takes a prospect (name, title, company) and produces a personalized outbound sales email draft with a fully visible reasoning trail. The human always reviews and approves before anything is sent.

## Tech Stack
- **Backend:** Python + FastAPI, SQLite via SQLAlchemy, plain Python pipeline (no workflow engine)
- **Frontend:** Plain HTML + CSS + JavaScript (no frameworks, no bundlers)
- **LLM:** Anthropic Claude (4 distinct prompt roles — extractor, verifier, writer, critic)
- **Search:** Tavily API
- **Scraping:** Python requests + BeautifulSoup

## Project Structure
```
zamp-ai-sdr/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app entry, CORS, router registration
│   │   ├── api/
│   │   │   ├── prospects.py           # POST /api/prospects
│   │   │   ├── runs.py                # GET /api/runs, /runs/{id}, /runs/{id}/status, /runs/{id}/retry
│   │   │   ├── drafts.py              # PATCH /api/drafts/{id}/review
│   │   │   └── metrics.py             # GET /api/metrics
│   │   ├── core/
│   │   │   └── config.py              # env var loading via pydantic-settings
│   │   ├── pipeline/
│   │   │   ├── orchestrator.py        # PipelineOrchestrator — stage order defined here only
│   │   │   ├── stage1_intake.py
│   │   │   ├── stage2_company_research.py
│   │   │   ├── stage3_individual_research.py
│   │   │   ├── stage4_extract_signals.py
│   │   │   ├── stage5_validate_signals.py
│   │   │   ├── stage6_persona_mapping.py
│   │   │   ├── stage7_pain_mapping.py
│   │   │   ├── stage8_hook_scoring.py
│   │   │   ├── stage9_draft_generation.py
│   │   │   ├── stage10_quality_scoring.py
│   │   │   └── stage11_routing.py
│   │   ├── llm/
│   │   │   ├── client.py              # thin Anthropic SDK wrapper
│   │   │   └── prompts/
│   │   │       ├── extractor.py
│   │   │       ├── verifier.py
│   │   │       ├── writer.py
│   │   │       └── critic.py
│   │   ├── services/
│   │   │   ├── search_service.py      # Tavily wrapper + retry/backoff
│   │   │   ├── scrape_service.py      # requests + BeautifulSoup + retry/backoff
│   │   │   ├── persona_library.py     # static persona data (CFO, Controller, etc.)
│   │   │   └── scoring.py             # hook score formula + rubric helpers
│   │   ├── models/
│   │   │   ├── db_models.py           # SQLAlchemy ORM models
│   │   │   └── schemas.py             # Pydantic request/response schemas
│   │   └── db/
│   │       ├── database.py            # engine + session setup
│   │       └── init_db.py             # creates tables on first run
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html                     # New Prospect screen (route: /)
│   ├── run.html                       # Live Run View + Review screen (route: /run.html?id=...)
│   ├── dashboard.html                 # Dashboard (route: /dashboard.html)
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── api.js                     # fetch wrapper for all backend calls
│       ├── intake.js
│       ├── run-view.js                # handles both live-progress and review states
│       └── dashboard.js
├── docs/
│   ├── BUSINESS_CONTEXT.md
│   └── TECHNICAL_SPEC.md
└── CLAUDE.md                          # this file
```

## Core Rules — Read Before Writing Any Code

1. **No hallucination tolerance.** Every factual claim in a generated email must trace to a stored signal with a verbatim `source_snippet`. The verifier stage (stage 5) is a hard gate, not a soft check.

2. **Pipeline stages are pure functions.** Each stage function takes typed Pydantic inputs and returns typed Pydantic outputs. Stages do not call each other — only the orchestrator does.

3. **The orchestrator is the only place stage order is defined.** Do not call stage functions from anywhere else.

4. **No business logic in the frontend.** All scoring, routing, and gating happens server-side. The frontend only renders what the backend returns.

5. **Every external call (LLM, search, scrape) gets retry + exponential backoff.** Default: 3 attempts, 1s / 2s / 4s delays. Failures are logged as `status='degraded'` — they never crash the pipeline.

6. **One regeneration cap on draft generation.** If the critic flags a groundedness failure, regenerate exactly once, then escalate to `needs_human_research`. No loops.

7. **Frontend is plain HTML/CSS/JS.** No React, no Vue, no build step. Use vanilla `fetch()` for API calls. Poll `/api/runs/{id}/status` every 1.5s while a run is in progress.

8. **API keys never leave the backend.** `.env` file, loaded server-side only. Never embedded in frontend JS.

9. **All inputs validated server-side with Pydantic.** Client-side validation is a UX nicety, not the trust boundary.

10. **Immutable audit trail.** Never update or delete `audit_log` or `review_actions` rows. Retries create new runs.

## Environment Variables
```
LLM_API_KEY=...
LLM_PROVIDER=anthropic
TAVILY_API_KEY=...
DATABASE_URL=sqlite:///./zamp_sdr.db
CORS_ALLOWED_ORIGIN=http://localhost:5500
SENDER_NAME=...
SENDER_TITLE=...
```

## Local Setup
```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in keys
python -m app.db.init_db
uvicorn app.main:app --reload --port 8000

# Frontend — open with any static file server
# e.g. VS Code Live Server, or: python -m http.server 5500 (from /frontend)
```

## Running Tests
```bash
cd backend
pytest tests/ -v
```
