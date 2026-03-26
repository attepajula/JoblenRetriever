import logging
import time
from abc import ABC, abstractmethod

import httpx

from ..db import upsert_job
from ..models import Job

logger = logging.getLogger(__name__)

UA = "JoblenRetriever/0.1 (job aggregator)"


class BaseScraper(ABC):
    def __init__(self, source_id: int, conn):
        self.source_id = source_id
        self.conn = conn
        self.client = httpx.Client(
            headers={"User-Agent": UA},
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )

    def _get(self, url: str, **kwargs) -> httpx.Response:
        return self._request("GET", url, **kwargs)

    def _post(self, url: str, **kwargs) -> httpx.Response:
        return self._request("POST", url, **kwargs)

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        for attempt in range(3):
            try:
                resp = self.client.request(method, url, **kwargs)
                resp.raise_for_status()
                return resp
            except httpx.HTTPStatusError as e:
                if e.response.status_code < 500 or attempt == 2:
                    raise
            except httpx.RequestError:
                if attempt == 2:
                    raise
            wait = 2 ** attempt
            logger.warning("Request failed, retrying %s in %ds (attempt %d/3)", url, wait, attempt + 2)
            time.sleep(wait)
        raise RuntimeError("unreachable")

    @abstractmethod
    def fetch_jobs(self) -> list[Job]:
        ...

    def run(self) -> int:
        jobs = self.fetch_jobs()
        for job in jobs:
            upsert_job(self.conn, job)
        logger.info("[%s] upserted %d jobs", self.__class__.__name__, len(jobs))
        return len(jobs)
