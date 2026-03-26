-- Rebuild FTS index: use 'simple' dictionary (works for Finnish + English)
-- and include company + location in the searchable vector
DROP INDEX IF EXISTS jobs_fts_idx;

CREATE INDEX jobs_fts_idx ON jobs USING GIN (
    to_tsvector('simple',
        title || ' ' ||
        company || ' ' ||
        COALESCE(location, '') || ' ' ||
        COALESCE(description, '')
    )
);
