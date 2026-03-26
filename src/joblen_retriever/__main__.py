import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .db import get_connection, get_source_id
from .scrapers.duunitori import DuunitoriScraper
from .scrapers.jobly import JoblyScraper
from .scrapers.remotive import RemotiveScraper
from .scrapers.tyomarkkinatori import TyomarkkinatoriScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

SCRAPERS = [
    ("remotive",        lambda sid, conn: RemotiveScraper(sid, conn, category="software-dev")),
    ("duunitori",       lambda sid, conn: DuunitoriScraper(sid, conn)),
    ("jobly",           lambda sid, conn: JoblyScraper(sid, conn)),
    ("tyomarkkinatori", lambda sid, conn: TyomarkkinatoriScraper(sid, conn)),
]


def _run_scraper(source_name: str, factory) -> int:
    conn = get_connection()
    try:
        source_id = get_source_id(conn, source_name)
        return factory(source_id, conn).run()
    except Exception:
        logger.exception("[%s] scraper failed", source_name)
        return 0
    finally:
        conn.close()


def main():
    with ThreadPoolExecutor(max_workers=len(SCRAPERS)) as pool:
        futures = {pool.submit(_run_scraper, name, factory): name for name, factory in SCRAPERS}
        total = sum(f.result() for f in as_completed(futures))
    logger.info("Done — %d jobs upserted across all sources", total)


if __name__ == "__main__":
    main()
