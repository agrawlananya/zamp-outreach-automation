import re

from app.models.schemas import CorpusItem, RawCorpus
from app.services import scrape_service, search_service

ROLE_CHANGE_PATTERN = re.compile(
    # Trigger phrase is case-insensitive; the captured company name must be Capitalized,
    # so this whole pattern can't use a blanket re.IGNORECASE (that would make [A-Z] match
    # any letter and swallow trailing lowercase words like "as" into the company name).
    r"((?i:joins|appointed at|moves to))\s+([A-Z][\w&.,'-]*(?:\s+[A-Z][\w&.,'-]*){0,3})"
)


def _detect_role_change(body_text: str, submitted_company_name: str) -> dict | None:
    match = ROLE_CHANGE_PATTERN.search(body_text)
    if not match:
        return None

    candidate_company = match.group(2).strip()
    if candidate_company.lower() == submitted_company_name.lower():
        return None

    return {"new_company": candidate_company, "trigger_phrase": match.group(1), "snippet": match.group(0)}


def research_individual(name: str, company_name: str) -> RawCorpus:
    # Both queries are anchored to the company, not just the name — a name-only query
    # ("{name} CFO OR Controller OR finance") readily surfaces an unrelated same-named
    # person at a different company, which is exactly the identity-mixing bug this stage
    # guards against below.
    queries = [
        f"{name} {company_name}",
        f"{name} {company_name} CFO OR Controller OR finance",
    ]

    seen_urls: set[str] = set()
    items: list[CorpusItem] = []
    role_change_detected = None

    for query in queries:
        for result in search_service.search(query):
            url = result["url"]
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            scraped = scrape_service.scrape(url)
            body_lower = scraped["body_text"].lower()

            if name.lower() not in body_lower:
                continue  # identity verification: discard if prospect's name isn't actually in the page

            role_change = _detect_role_change(scraped["body_text"], company_name)

            if company_name.lower() not in body_lower and role_change is None:
                # The page never mentions the submitted company, and doesn't look like a
                # legitimate "moved to a new company" case either — most likely a different
                # person who happens to share this name. Discard rather than mix identities.
                continue

            items.append(
                CorpusItem(
                    url=scraped["url"],
                    title=scraped["title"],
                    body_text=scraped["body_text"],
                    published_date=result.get("published_date"),
                )
            )

            if role_change_detected is None and role_change:
                role_change_detected = {**role_change, "source_url": scraped["url"]}

    non_empty_count = sum(1 for item in items if item.body_text)
    return RawCorpus(
        source="individual",
        items=items,
        thin_corpus=non_empty_count < 2,
        role_change_detected=role_change_detected,
    )
