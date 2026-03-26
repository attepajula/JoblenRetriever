import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

from .models import Job

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 5432)),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ.get("DB_PASSWORD", ""),
    )


@contextmanager
def get_cursor(conn):
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def upsert_job(conn, job: Job) -> None:
    sql = """
        INSERT INTO jobs (
            source_id, external_id, title, company, location,
            url, description, tags, salary_range, posted_at, scraped_at, country
        ) VALUES (
            %(source_id)s, %(external_id)s, %(title)s, %(company)s, %(location)s,
            %(url)s, %(description)s, %(tags)s, %(salary_range)s, %(posted_at)s, NOW(), %(country)s
        )
        ON CONFLICT (source_id, external_id) DO UPDATE SET
            title        = EXCLUDED.title,
            company      = EXCLUDED.company,
            location     = EXCLUDED.location,
            url          = EXCLUDED.url,
            description  = EXCLUDED.description,
            tags         = EXCLUDED.tags,
            salary_range = EXCLUDED.salary_range,
            posted_at    = EXCLUDED.posted_at,
            scraped_at   = NOW(),
            country      = EXCLUDED.country,
            is_active    = TRUE
    """
    with get_cursor(conn) as cur:
        cur.execute(sql, {
            "source_id":   job.source_id,
            "external_id": job.external_id,
            "title":       job.title,
            "company":     job.company,
            "location":    job.location,
            "url":         job.url,
            "description": job.description,
            "tags":        job.tags,
            "salary_range": job.salary_range,
            "posted_at":   job.posted_at,
            "country":     job.country,
        })


def get_source_id(conn, name: str) -> int:
    with get_cursor(conn) as cur:
        cur.execute("SELECT id FROM sources WHERE name = %s", (name,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Source '{name}' not found. Run schema.sql first.")
        return row["id"]
