import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import drafts, metrics, prospects, runs
from app.core.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(title="Zamp AI SDR")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(prospects.router)
app.include_router(runs.router)
app.include_router(drafts.router)
app.include_router(metrics.router)


@app.get("/health")
def health():
    return {"status": "ok"}
