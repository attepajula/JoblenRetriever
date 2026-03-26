# JoblenRetriever

A job search aggregator that scrapes job listings and stores them in a PostgreSQL database, with a future Rust backend and Ollama-powered chat interface for production use.

## Project Vision

- **Phase 1 (current):** Python web scrapers + PostgreSQL database + FastAPI
- **Phase 2 (future):** Rust backend API
- **Phase 3 (future):** Ollama chat interface for AI-assisted job search

## Tech Stack

### Current
- **Language:** Python (uv for dependency management)
- **Database:** PostgreSQL (`joblen` db, user `attepajula`, no password)
- **Scraping:** `requests` + `BeautifulSoup` for static HTML; `Playwright` (Chromium) for JS-rendered sites
- **API:** FastAPI + Uvicorn, runs on `http://127.0.0.1:8000`
- **Entry points:** `uv run joblen-run` (scraper), `uv run joblen-api` (API server)

### Future
- **Backend:** Rust
- **AI Interface:** Ollama (local LLM chat)

## Project Structure

```
JoblenRetriever/
├── CLAUDE.md
├── pyproject.toml
├── .env                  # DB credentials (not committed)
├── .env.example
├── sql/
│   ├── schema.sql        # Full schema (for fresh installs)
│   └── migrations/
│       └── 001_add_country_and_sources.sql
└── src/joblen_retriever/
    ├── models.py         # Job + Source dataclasses
    ├── db.py             # Connection, upsert_job, get_source_id
    ├── api.py            # FastAPI endpoints
    ├── server.py         # Uvicorn entrypoint
    ├── __main__.py       # Runs all scrapers
    └── scrapers/
        ├── base.py            # BaseScraper (requests-based)
        ├── playwright_base.py # PlaywrightBaseScraper
        ├── remotive.py        # Remotive.com public API (INTL)
        ├── duunitori.py       # Duunitori.fi HTML scraper (FI) ✅ 270 jobs
        ├── jobly.py           # Jobly.fi HTML scraper (FI) — selectors fixed
        └── tyomarkkinatori.py # Työmarkkinatori REST API (FI) — API found
```

## Sources & Status

| Source | Method | Country | Status |
|--------|--------|---------|--------|
| Remotive | Public JSON API | INTL | ✅ Working |
| Duunitori | requests + BS4 (`article` → `.node--job-per-template`) | FI | ✅ Working |
| Jobly | requests + BS4 (`article.node--job-per-template`, `a.recruiter-job-link`) | FI | Fixing |
| Työmarkkinatori | REST API POST `/api/jobpostingfulltext/search/v2/search` | FI | Rewriting (no Playwright needed) |

## Key API Details

### Työmarkkinatori
- **Endpoint:** `POST https://tyomarkkinatori.fi/api/jobpostingfulltext/search/v2/search`
- **Headers:** `content-type: application/json`, `referer: https://tyomarkkinatori.fi/`
- **Body:** `{"query":"","filters":{},"paging":{"pageNumber":0,"pageSize":30},"sorting":"LATEST"}`
- **Response:** `{pageSize, totalElements, lastPage, content: [{id, employer, title, applicationUrl, location, publishDate, tags, ...}]}`
- `title` and `applicationUrl` are objects with language keys: `{"fi": "..."}`
- `employer.ownerName.fi` is the company name
- `location.municipalities[].label.fi` for city names

### Duunitori
- Listing URL: `https://duunitori.fi/tyopaikat?sivu=N`
- Card: `div.job-box`, title: `.job-box__title`, location: `.job-box__job-location`, date: `.job-box__job-posted`, link: `a.job-box__hover`

### Jobly
- Listing URL: `https://www.jobly.fi/tyopaikat?page=N`
- Card: `article.node--job-per-template`, ID from `article[id]` (`node-XXXXXXX`)
- Title: `a.recruiter-job-link[title]`, company: `span.recruiter-company-profile-job-organization a`, location: `div.location`, date: `span.date`

## DB Schema

Tables: `sources` (id, name, base_url, country), `jobs` (id, source_id, external_id, title, company, location, url, description, tags[], salary_range, posted_at, scraped_at, is_active, country)

## Conventions

- Use `uv` for Python dependency management
- Store secrets in `.env` (never commit)
- Schema in `sql/schema.sql`, migrations in `sql/migrations/`
- Each job board gets its own scraper module
- `country='FI'` for Finnish sources, `country='INTL'` for international
- Scrapers are idempotent — safe to re-run, uses `ON CONFLICT DO UPDATE`
