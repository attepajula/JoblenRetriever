# Joblen

A job search aggregator for tech roles in Finland and beyond. Scrapes multiple job boards into a single PostgreSQL database and surfaces them through a clean, fast search UI.

## What it does

- Aggregates tech job listings from Finnish and international job boards
- Full-text prefix search — results appear as you type
- Filter by country (Finland / International / All)
- Smart description trimming — skips company intro boilerplate, gets straight to the role
- FastAPI backend · React + Tailwind frontend · PostgreSQL with FTS indexes

## Stack

| Layer | Tech |
|---|---|
| Language | Python 3.11+ (uv) |
| Scraping | httpx + BeautifulSoup, Scrapy |
| Database | PostgreSQL (full-text search via `tsvector`) |
| API | FastAPI + Uvicorn |
| Frontend | React + Vite + TypeScript + Tailwind CSS v4 |

## Sources

| Source | Country |
|---|---|
| LinkedIn | FI / INTL |
| Duunitori | FI |
| Jobly | FI |
| Työmarkkinatori | FI |
| Remotive | INTL |

## Getting started

**Requirements:** Python 3.11+, PostgreSQL, [uv](https://docs.astral.sh/uv/), Node.js

```bash
# Install dependencies
uv sync

# Set up environment
cp .env.example .env
# edit .env with your DB credentials

# Set up database
psql -d joblen -f sql/schema.sql
psql -d joblen -f sql/migrations/001_add_country_and_sources.sql
psql -d joblen -f sql/migrations/002_update_fts_index.sql
psql -d joblen -f sql/migrations/003_add_crawler_sources.sql
```

```bash
# Run scrapers (Duunitori, Jobly, Tyomarkkinatori, Remotive)
uv run joblen-run

# Run crawler (LinkedIn)
uv run joblen-crawl

# Start API
uv run joblen-api

# Start frontend (separate terminal)
cd frontend && npm install && npm run dev
```

API runs at `http://127.0.0.1:8000`, frontend at `http://localhost:5173`.

## Project structure

```
src/joblen_retriever/
├── api.py              # FastAPI endpoints
├── db.py               # PostgreSQL connection + upsert
├── models.py           # Job dataclass
├── scrapers/           # httpx-based scrapers (Duunitori, Jobly, etc.)
└── crawlers/           # Scrapy-based crawler (LinkedIn)

frontend/src/
├── App.tsx             # Main app, search + pagination
├── api.ts              # Fetch wrapper
├── components/
│   ├── JobCard.tsx     # Job listing card
│   └── JobDetail.tsx   # Job detail modal
└── types.ts

sql/
├── schema.sql          # Full schema
└── migrations/         # Incremental migrations
```

## Roadmap

- [ ] Rust backend API (Phase 2)
- [ ] Ollama chat interface for AI-assisted job search (Phase 3)
- [ ] More sources
- [ ] Email / RSS alerts

## License

MIT
