import re
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from ..models import Job
from .base import BaseScraper

BASE_URL = "https://duunitori.fi"
JOBS_URL = f"{BASE_URL}/tyopaikat"


class DuunitoriScraper(BaseScraper):
    def __init__(self, source_id: int, conn, max_pages: int = 10):
        super().__init__(source_id, conn)
        self.max_pages = max_pages
        self.client.headers.update({"Accept-Language": "fi-FI,fi;q=0.9"})

    def fetch_jobs(self) -> list[Job]:
        jobs = []
        for page_num in range(self.max_pages):
            params = {} if page_num == 0 else {"sivu": page_num + 1}
            resp = self._get(JOBS_URL, params=params)
            soup = BeautifulSoup(resp.text, "html.parser")

            cards = soup.select("div.job-box, a.job-box")
            if not cards:
                break

            for card in cards:
                link_el = card.select_one("a.job-box__hover") or (
                    card if card.name == "a" else None
                )
                title_el = card.select_one(".job-box__title")
                location_el = card.select_one(".job-box__job-location")
                date_el = card.select_one(".job-box__job-posted")
                logo_el = card.select_one("img.job-box__logo")
                salary_el = card.select_one(".tag--salary")

                if not title_el or not link_el:
                    continue

                href = link_el.get("href", "")
                url = BASE_URL + href
                external_id = _extract_id(href)

                company = ""
                if logo_el:
                    alt = logo_el.get("alt", "")
                    company = re.sub(r"\s*logo\s*$", "", alt, flags=re.IGNORECASE).strip()

                jobs.append(Job(
                    source_id=self.source_id,
                    external_id=external_id or href,
                    title=title_el.get_text(strip=True),
                    company=company,
                    location=location_el.get_text(strip=True) if location_el else None,
                    url=url,
                    salary_range=salary_el.get_text(strip=True) if salary_el else None,
                    posted_at=_parse_fi_date(date_el.get_text(strip=True)) if date_el else None,
                    country="FI",
                ))

        return jobs


def _extract_id(href: str) -> str:
    """Extract numeric job ID from slug like /tyopaikat/tyo/title-srsen-20117178."""
    m = re.search(r"-(\d+)$", href)
    return m.group(1) if m else href.rsplit("/", 1)[-1]


def _parse_fi_date(text: str) -> datetime | None:
    """Parse Duunitori date text like 'Julkaistu 23.3.' or 'Julkaistu tänään'."""
    text = re.sub(r"^Julkaistu\s*", "", text, flags=re.IGNORECASE).strip()
    if text.lower() in ("tänään", "idag", "today"):
        return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    m = re.match(r"(\d{1,2})\.(\d{1,2})\.?(?:\s*(\d{4}))?", text)
    if m:
        day, month = int(m.group(1)), int(m.group(2))
        year = int(m.group(3)) if m.group(3) else datetime.now().year
        try:
            return datetime(year, month, day, tzinfo=timezone.utc)
        except ValueError:
            pass
    return None
