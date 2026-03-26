from datetime import datetime, timezone

from ..models import Job
from .base import BaseScraper

API_URL = "https://tyomarkkinatori.fi/api/jobpostingfulltext/search/v2/search"
JOB_URL = "https://tyomarkkinatori.fi/henkiloasiakkaat/avoimet-tyopaikat/haku/{id}"
PAGE_SIZE = 30


class TyomarkkinatoriScraper(BaseScraper):
    def __init__(self, source_id: int, conn, max_pages: int = 20):
        super().__init__(source_id, conn)
        self.max_pages = max_pages
        self.client.headers.update({
            "referer": "https://tyomarkkinatori.fi/",
            "content-type": "application/json",
        })

    def fetch_jobs(self) -> list[Job]:
        jobs = []
        for page_num in range(self.max_pages):
            resp = self._post(
                API_URL,
                json={
                    "query": "",
                    "filters": {},
                    "paging": {"pageNumber": page_num, "pageSize": PAGE_SIZE},
                    "sorting": "LATEST",
                },
            )
            data = resp.json()

            for item in data.get("content", []):
                jobs.append(_parse_item(item, self.source_id))

            if page_num >= data.get("lastPage", 0):
                break

        return jobs


def _parse_item(item: dict, source_id: int) -> Job:
    ext_id = item["id"]

    title = _fi(item.get("title")) or ""
    company = (
        _fi(item.get("employer", {}).get("ownerName"))
        or item.get("employer", {}).get("name", "")
    )

    municipalities = item.get("location", {}).get("municipalities", [])
    location = ", ".join(m["label"]["fi"] for m in municipalities if m.get("label", {}).get("fi"))

    app_url = _fi(item.get("applicationUrl", {}).get("values")) or ""
    url = app_url or JOB_URL.format(id=ext_id)

    published = item.get("publishDate")

    return Job(
        source_id=source_id,
        external_id=ext_id,
        title=title,
        company=company,
        location=location or None,
        url=url,
        tags=item.get("tags") or [],
        posted_at=_parse_date(published),
        country="FI",
    )


def _fi(obj) -> str:
    """Extract Finnish value from a {fi, sv, en} dict."""
    if isinstance(obj, dict):
        return obj.get("fi") or obj.get("en") or next(iter(obj.values()), "") or ""
    return obj or ""


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.rstrip("Z")).replace(tzinfo=timezone.utc)
    except ValueError:
        return None
