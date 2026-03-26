from datetime import datetime, timezone

from bs4 import BeautifulSoup

from ..models import Job
from .base import BaseScraper

API_URL = "https://remotive.com/api/remote-jobs"


class RemotiveScraper(BaseScraper):
    def __init__(self, source_id: int, conn, category: str | None = None):
        super().__init__(source_id, conn)
        self.category = category  # e.g. "software-dev", "devops-sysadmin"

    def fetch_jobs(self) -> list[Job]:
        params = {}
        if self.category:
            params["category"] = self.category

        resp = self._get(API_URL, params=params)
        data = resp.json()

        jobs = []
        for item in data.get("jobs", []):
            jobs.append(Job(
                source_id=self.source_id,
                external_id=str(item["id"]),
                title=item["title"],
                company=item["company_name"],
                location=item.get("candidate_required_location") or None,
                url=item["url"],
                description=_strip_html(item.get("description", "")),
                tags=item.get("tags") or [],
                salary_range=item.get("salary") or None,
                posted_at=_parse_date(item.get("publication_date")),
                country="INTL",
            ))
        return jobs


def _strip_html(html: str) -> str:
    if not html:
        return ""
    return BeautifulSoup(html, "html.parser").get_text(separator="\n").strip()


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    except ValueError:
        return None
