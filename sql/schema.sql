CREATE TABLE IF NOT EXISTS sources (
    id         SERIAL PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE,
    base_url   TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS jobs (
    id          SERIAL PRIMARY KEY,
    source_id   INTEGER NOT NULL REFERENCES sources(id),
    external_id TEXT    NOT NULL,
    title       TEXT    NOT NULL,
    company     TEXT    NOT NULL,
    location    TEXT,
    url         TEXT    NOT NULL,
    description TEXT,
    tags        TEXT[]  NOT NULL DEFAULT '{}',
    salary_range TEXT,
    posted_at   TIMESTAMPTZ,
    scraped_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active   BOOLEAN     NOT NULL DEFAULT TRUE,

    CONSTRAINT jobs_source_external_unique UNIQUE (source_id, external_id)
);

CREATE INDEX IF NOT EXISTS jobs_posted_at_idx  ON jobs (posted_at DESC);
CREATE INDEX IF NOT EXISTS jobs_company_idx    ON jobs (company);
CREATE INDEX IF NOT EXISTS jobs_source_idx     ON jobs (source_id);
CREATE INDEX IF NOT EXISTS jobs_tags_idx       ON jobs USING GIN (tags);
CREATE INDEX IF NOT EXISTS jobs_fts_idx        ON jobs USING GIN (
    to_tsvector('english', title || ' ' || COALESCE(description, ''))
);

-- Seed known sources
INSERT INTO sources (name, base_url) VALUES
    ('remotive', 'https://remotive.com')
ON CONFLICT (name) DO NOTHING;
