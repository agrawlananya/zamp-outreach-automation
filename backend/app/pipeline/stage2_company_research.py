from app.models.schemas import CorpusItem, RawCorpus
from app.services import scrape_service, search_service


def research_company(domain: str, company_name: str, prospect_name: str) -> RawCorpus:
    queries = [
        # Anchored to the prospect's name first, to bias results toward the specific company
        # tied to this specific person rather than an unrelated company/product sharing the name.
        f"{company_name} {prospect_name}",
        f"{company_name} news",
        f"{company_name} CFO OR finance OR funding",
        f"{company_name} hiring OR layoffs OR expansion",
    ]

    seen_urls: set[str] = set()
    items: list[CorpusItem] = []

    for query in queries:
        for result in search_service.search(query):
            url = result["url"]
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            scraped = scrape_service.scrape(url)
            items.append(
                CorpusItem(
                    url=scraped["url"],
                    title=scraped["title"],
                    body_text=scraped["body_text"],
                    published_date=result.get("published_date"),
                )
            )

    non_empty_count = sum(1 for item in items if item.body_text)
    return RawCorpus(source="company", items=items, thin_corpus=non_empty_count < 2)
