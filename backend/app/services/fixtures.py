import json
from pathlib import Path

from app.models.schemas import RawCorpus

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


class FixtureNotFoundError(Exception):
    pass


def load_fixture(fixture_id: str) -> tuple[RawCorpus, RawCorpus]:
    """FIXTURE MODE: replays a stored research payload instead of live Tavily/scrape calls,
    so the *research* is pinned and reproducible. Everything downstream of stage 2 (extraction,
    validation, role confirmation, pain mapping, hook scoring, draft, critic) still runs live
    against this fixed input — only the research data is pinned, not the LLM outputs."""
    path = FIXTURES_DIR / f"{fixture_id}.json"
    if not path.exists():
        raise FixtureNotFoundError(f"No fixture found for fixture_id={fixture_id!r}")

    data = json.loads(path.read_text(encoding="utf-8"))
    company_corpus = RawCorpus.model_validate(data["company_corpus"])
    individual_corpus = RawCorpus.model_validate(data["individual_corpus"])
    return company_corpus, individual_corpus


def list_fixture_ids() -> list[str]:
    if not FIXTURES_DIR.exists():
        return []
    return sorted(p.stem for p in FIXTURES_DIR.glob("*.json"))
