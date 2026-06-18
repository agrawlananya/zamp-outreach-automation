import logging
import time

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

RETRY_DELAYS_SECONDS = [1, 2, 4]
MAX_BODY_TEXT_LENGTH = 8000
REQUEST_TIMEOUT_SECONDS = 10


def scrape(url: str) -> dict:
    last_error: Exception | None = None
    for attempt, delay in enumerate(RETRY_DELAYS_SECONDS):
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup(["script", "style"]):
                tag.decompose()

            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            body_text = soup.get_text(separator=" ", strip=True)[:MAX_BODY_TEXT_LENGTH]

            return {"url": url, "title": title, "body_text": body_text}
        except Exception as e:
            last_error = e
            if attempt < len(RETRY_DELAYS_SECONDS) - 1:
                time.sleep(delay)

    logger.error("scrape failed after %d attempts for url=%r: %s", len(RETRY_DELAYS_SECONDS), url, last_error)
    return {"url": url, "title": "", "body_text": "", "error": str(last_error)}
