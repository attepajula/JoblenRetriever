import re
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from ..models import Job
from .base import BaseScraper

BASE_URL = "https://www.jobly.fi"
JOBS_URL = f"{BASE_URL}/tyopaikat"


class JoblyScraper(BaseScraper):
    def __init__(self, source_id: int, conn, max_pages: int = 10):
        super().__init__(source_id, conn)
        self.max_pages = max_pages
        self.client.headers.update({"Accept-Language": "fi-FI,fi;q=0.9"})

    def fetch_jobs(self) -> list[Job]:
        jobs = []
        for page_num in range(self.max_pages):
            params = {} if page_num == 0 else {"page": page_num}
            resp = self._get(JOBS_URL, params=params)
            soup = BeautifulSoup(resp.text, "html.parser")

            cards = soup.select("article.node--job-per-template")
            if not cards:
                break

            for card in cards:
                link_el = card.select_one("a.recruiter-job-link")
                company_el = card.select_one("span.recruiter-company-profile-job-organization a")
                location_el = card.select_one("div.location")
                date_el = card.select_one("span.date")

                if not link_el:
                    continue

                href = link_el.get("href", "")
                url = href if href.startswith("http") else BASE_URL + href
                title = link_el.get("title") or link_el.get_text(strip=True)

                # External ID from article id attribute: "node-2625315" -> "2625315"
                node_id = card.get("id", "")
                external_id = node_id.replace("node-", "") if node_id else _extract_id(href)

                jobs.append(Job(
                    source_id=self.source_id,
                    external_id=external_id,
                    title=title,
                    company=company_el.get_text(strip=True) if company_el else "",
                    location=location_el.get_text(strip=True) if location_el else None,
                    url=url,
                    posted_at=_parse_fi_date(date_el.get_text(strip=True)) if date_el else None,
                    country="FI",
                ))

            # Stop if no next-page link
            if not soup.select_one(".pager__item--next a"):
                break

        return jobs


def _extract_id(href: str) -> str:
    m = re.search(r"-(\d+)(?:/.*)?$", href)
    return m.group(1) if m else href.rsplit("/", 1)[-1]


def _parse_fi_date(text: str) -> datetime | None:
    text = text.strip().rstrip(",")
    m = re.match(r"(\d{1,2})\.(\d{1,2})\.(\d{2,4})", text)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if year < 100:
            year += 2000
        try:
            return datetime(year, month, day, tzinfo=timezone.utc)
        except ValueError:
            pass
    return None
