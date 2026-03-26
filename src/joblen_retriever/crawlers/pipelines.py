import logging

from ..db import get_connection, get_source_id, upsert_job
from ..models import Job

logger = logging.getLogger(__name__)


class PostgresPipeline:
    def open_spider(self, spider):
        self.conn = get_connection()
        self._source_cache: dict[str, int] = {}

    def close_spider(self, spider):
        self.conn.close()

    def _get_source_id(self, name: str) -> int:
        if name not in self._source_cache:
            self._source_cache[name] = get_source_id(self.conn, name)
        return self._source_cache[name]

    def process_item(self, item, spider):
        source_id = self._get_source_id(item["source_name"])
        job = Job(
            source_id=source_id,
            external_id=item["external_id"],
            title=item["title"],
            company=item.get("company") or "",
            location=item.get("location"),
            url=item["url"],
            description=item.get("description"),
            tags=item.get("tags") or [],
            salary_range=item.get("salary_range"),
            posted_at=item.get("posted_at"),
            country=item.get("country"),
        )
        upsert_job(self.conn, job)
        return item
