import re
from dataclasses import dataclass

from app.llm.client import call_llm
from app.llm.parsing import parse_json_response
from app.llm.prompts.role_confirmation import build_role_confirmation_prompt
from app.models.schemas import CorpusItem, RawCorpus
from app.services import scrape_service, search_service
from app.services.concurrency import run_concurrently

MAX_URLS_TO_SCRAPE = 12
MAX_ROLE_CONFIRMATION_TEXT_LENGTH = 6000

ROLE_CHANGE_PATTERN = re.compile(
    # Trigger phrase is case-insensitive; the captured company name must be Capitalized,
    # so this whole pattern can't use a blanket re.IGNORECASE (that would make [A-Z] match
    # any letter and swallow trailing lowercase words like "as" into the company name).
    r"((?i:joins|appointed at|moves to))\s+([A-Z][\w&.,'-]*(?:\s+[A-Z][\w&.,'-]*){0,3})"
)

# Scraped pages can contain unrelated content (nav menus, "latest news" sidebars) far from
# the actual article. A bare page-wide regex search will false-trigger on a "X joins Y"
# headline about a completely different person. Requiring the prospect's name to appear
# within this many characters of the match anchors the detection to text that's actually
# about them, without needing sentence/paragraph boundaries (scrape_service flattens those).
NAME_PROXIMITY_WINDOW_CHARS = 300


def _detect_role_change(body_text: str, submitted_company_name: str, name: str) -> dict | None:
    name_lower = name.lower()

    for match in ROLE_CHANGE_PATTERN.finditer(body_text):
        window_start = max(0, match.start() - NAME_PROXIMITY_WINDOW_CHARS)
        window_end = match.end() + NAME_PROXIMITY_WINDOW_CHARS
        if name_lower not in body_text[window_start:window_end].lower():
            continue

        candidate_company = match.group(2).strip()
        if candidate_company.lower() == submitted_company_name.lower():
            continue

        return {"new_company": candidate_company, "trigger_phrase": match.group(1), "snippet": match.group(0)}

    return None


def research_prospect(name: str, company_name: str) -> tuple[RawCorpus, RawCorpus]:
    queries = [
        f"{company_name} {name}",
        f"{company_name} {name} interview OR quote OR announcement",
        f"{company_name} news",
        f"{company_name} growth OR expansion OR hiring",
        f"{company_name} funding OR investment OR acquisition",
        f"{name} {company_name} role OR initiative OR announcement",
    ]

    # Queries are ordered most-specific-first, so dedup-and-cap here keeps the
    # highest-value URLs rather than truncating arbitrarily.
    seen_urls: set[str] = set()
    queued_results: list[dict] = []
    for query in queries:
        for result in search_service.search(query):
            url = result["url"]
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            queued_results.append(result)
            if len(queued_results) >= MAX_URLS_TO_SCRAPE:
                break
        if len(queued_results) >= MAX_URLS_TO_SCRAPE:
            break

    scraped_pages = run_concurrently(lambda r: scrape_service.scrape(r["url"]), queued_results, max_workers=5)

    company_items: list[CorpusItem] = []
    individual_items: list[CorpusItem] = []
    role_change_detected = None

    for result, scraped in zip(queued_results, scraped_pages):
        body_lower = scraped["body_text"].lower()

        item = CorpusItem(
            url=scraped["url"],
            title=scraped["title"],
            body_text=scraped["body_text"],
            published_date=result.get("published_date"),
        )

        if name.lower() not in body_lower:
            if company_name.lower() in body_lower:
                company_items.append(item)
            continue

        role_change = _detect_role_change(scraped["body_text"], company_name, name)

        if company_name.lower() not in body_lower and role_change is None:
            # The page never mentions the submitted company, and doesn't look like a
            # legitimate "moved to a new company" case either — most likely a different
            # person who happens to share this name. Discard rather than mix identities.
            continue

        individual_items.append(item)

        if role_change_detected is None and role_change:
            role_change_detected = {**role_change, "source_url": scraped["url"]}

    company_non_empty = sum(1 for item in company_items if item.body_text)
    individual_non_empty = sum(1 for item in individual_items if item.body_text)

    company_corpus = RawCorpus(
        source="company",
        items=company_items,
        thin_corpus=company_non_empty < 2,
    )
    individual_corpus = RawCorpus(
        source="individual",
        items=individual_items,
        thin_corpus=individual_non_empty < 2,
        role_change_detected=role_change_detected,
    )

    return company_corpus, individual_corpus


NEW_IN_ROLE_THRESHOLD_DAYS = 90


@dataclass
class RoleConfirmationResult:
    confirmed_title: str | None
    tenure_days: int | None
    left_company: bool
    title_confirmed: bool


def confirm_role(individual_corpus: RawCorpus, name: str, company_name: str, input_title: str) -> RoleConfirmationResult:
    """Edge case: STALE SEAT. The submitted title is an unverified hypothesis — check it
    against the individual-scoped research already gathered (no new search/scrape calls)."""
    individual_text = "\n\n".join(item.body_text for item in individual_corpus.items if item.body_text)
    individual_text = individual_text[:MAX_ROLE_CONFIRMATION_TEXT_LENGTH]

    if not individual_text:
        return RoleConfirmationResult(confirmed_title=None, tenure_days=None, left_company=False, title_confirmed=False)

    system_prompt, user_prompt = build_role_confirmation_prompt(individual_text, name, company_name, input_title)
    try:
        response = call_llm(system_prompt, user_prompt)
        parsed = parse_json_response(response)
    except Exception:
        # Can't confirm — caller treats this the same as "role cannot be confirmed either way".
        return RoleConfirmationResult(confirmed_title=None, tenure_days=None, left_company=False, title_confirmed=False)

    return RoleConfirmationResult(
        confirmed_title=parsed.get("confirmed_title"),
        tenure_days=parsed.get("tenure_days"),
        left_company=bool(parsed.get("left_company", False)),
        title_confirmed=bool(parsed.get("title_confirmed", False)),
    )
