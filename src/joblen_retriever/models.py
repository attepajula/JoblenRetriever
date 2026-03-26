from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Source:
    id: int
    name: str
    base_url: str


@dataclass
class Job:
    source_id: int
    external_id: str
    title: str
    company: str
    url: str
    location: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    salary_range: str | None = None
    posted_at: datetime | None = None
    country: str | None = None
