from datetime import datetime

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

from .db import get_connection, get_cursor

app = FastAPI(title="JoblenRetriever", version="0.1.0")


class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: str | None
    url: str
    tags: list[str]
    salary_range: str | None
    posted_at: datetime | None
    scraped_at: datetime
    country: str | None


@app.get("/jobs", response_model=list[JobOut])
def list_jobs(
    q: str | None = Query(None, description="Full-text search"),
    company: str | None = Query(None),
    location: str | None = Query(None),
    tag: str | None = Query(None),
    country: str | None = Query(None, description="e.g. FI or INTL"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    filters = []
    params: dict = {"limit": limit, "offset": offset}

    if q:
        filters.append(
            "to_tsvector('english', title || ' ' || COALESCE(description, '')) "
            "@@ websearch_to_tsquery('english', %(q)s)"
        )
        params["q"] = q
    if company:
        filters.append("company ILIKE %(company)s")
        params["company"] = f"%{company}%"
    if location:
        filters.append("location ILIKE %(location)s")
        params["location"] = f"%{location}%"
    if tag:
        filters.append("%(tag)s = ANY(tags)")
        params["tag"] = tag
    if country:
        filters.append("country = %(country)s")
        params["country"] = country.upper()

    where = ("WHERE " + " AND ".join(filters)) if filters else ""
    sql = f"""
        SELECT id, title, company, location, url, tags, salary_range, posted_at, scraped_at, country
        FROM jobs
        {where}
        ORDER BY posted_at DESC NULLS LAST
        LIMIT %(limit)s OFFSET %(offset)s
    """

    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


@app.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int):
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "SELECT id, title, company, location, url, tags, salary_range, posted_at, scraped_at, country "
                "FROM jobs WHERE id = %s",
                (job_id,),
            )
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Job not found")
            return dict(row)
    finally:
        conn.close()
