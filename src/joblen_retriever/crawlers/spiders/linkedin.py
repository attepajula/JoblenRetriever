import re
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode

import scrapy
from bs4 import BeautifulSoup

from ...crawlers.items import JobItem

# LinkedIn guest job search — no login required
BASE = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

# Searches to run — extend freely
SEARCHES = [
    {"keywords": "software engineer",      "location": "Finland"},
    {"keywords": "backend developer",       "location": "Finland"},
    {"keywords": "frontend developer",      "location": "Finland"},
    {"keywords": "full stack developer",    "location": "Finland"},
    {"keywords": "data engineer",           "location": "Finland"},
    {"keywords": "devops engineer",         "location": "Finland"},
    {"keywords": "machine learning",        "location": "Finland"},
    {"keywords": "software engineer",       "location": "Remote"},
]

PAGE_SIZE = 25


class LinkedInSpider(scrapy.Spider):
    name = "linkedin"
    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def start_requests(self):
        for search in SEARCHES:
            url = BASE + "?" + urlencode({**search, "start": 0})
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={"search": search, "start": 0},
                headers={"Referer": "https://www.linkedin.com/"},
            )

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("li")

        for card in cards:
            item = _parse_card(card)
            if item:
                yield item

        # Paginate if we got a full page
        if len(cards) >= PAGE_SIZE:
            meta = response.meta
            next_start = meta["start"] + PAGE_SIZE
            url = BASE + "?" + urlencode({**meta["search"], "start": next_start})
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={"search": meta["search"], "start": next_start},
                headers={"Referer": "https://www.linkedin.com/"},
            )


def _parse_card(card) -> JobItem | None:
    title_el   = card.select_one(".base-search-card__title")
    company_el = card.select_one(".base-search-card__subtitle")
    location_el = card.select_one(".job-search-card__location")
    link_el    = card.select_one("a.base-card__full-link, a[data-tracking-id]")
    date_el    = card.select_one("time")

    if not title_el or not link_el:
        return None

    href = link_el.get("href", "").split("?")[0]
    external_id = _extract_id(href)
    if not external_id:
        return None

    return JobItem(
        source_name="linkedin",
        external_id=external_id,
        title=title_el.get_text(strip=True),
        company=company_el.get_text(strip=True) if company_el else "",
        location=location_el.get_text(strip=True) if location_el else None,
        url=href,
        tags=[],
        posted_at=_parse_date(date_el.get("datetime", "")) if date_el else None,
        country=_infer_country(location_el.get_text(strip=True) if location_el else ""),
    )


def _extract_id(href: str) -> str:
    m = re.search(r"-(\d+)/?$", href)
    return m.group(1) if m else ""


def _infer_country(location: str) -> str:
    location_lower = location.lower()
    if any(x in location_lower for x in ("finland", "suomi", "helsinki", "tampere", "espoo", "oulu", "turku")):
        return "FI"
    if "remote" in location_lower:
        return "INTL"
    return "INTL"


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    except ValueError:
        pass
    # relative: "2 weeks ago"
    m = re.match(r"(\d+)\s+(second|minute|hour|day|week|month)", value)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        delta = {
            "second": timedelta(seconds=n),
            "minute": timedelta(minutes=n),
            "hour":   timedelta(hours=n),
            "day":    timedelta(days=n),
            "week":   timedelta(weeks=n),
            "month":  timedelta(days=n * 30),
        }.get(unit, timedelta())
        return datetime.now(timezone.utc) - delta
    return None
