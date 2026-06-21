import logging
import time

from tavily import TavilyClient

from app.core.config import settings

logger = logging.getLogger(__name__)

RETRY_DELAYS_SECONDS = [1, 2, 4]

_client = TavilyClient(api_key=settings.TAVILY_API_KEY)


def search(
    query: str,
    max_results: int = 5,
    include_domains: list[str] | None = None,
    include_raw_content: bool = False,
) -> list[dict]:
    last_error: Exception | None = None
    for attempt, delay in enumerate(RETRY_DELAYS_SECONDS):
        try:
            extra: dict = {}
            if include_domains:
                extra["include_domains"] = include_domains
            if include_raw_content:
                extra["include_raw_content"] = True
            response = _client.search(query=query, max_results=max_results, **extra)
            results = response.get("results", [])
            return [
                {
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "content": r.get("raw_content") or r.get("content", ""),
                    "published_date": r.get("published_date"),
                }
                for r in results
            ]
        except Exception as e:
            last_error = e
            if attempt < len(RETRY_DELAYS_SECONDS) - 1:
                time.sleep(delay)
    logger.error("search failed after %d attempts for query=%r: %s", len(RETRY_DELAYS_SECONDS), query, last_error)
    return []
