-- Add country column to sources
ALTER TABLE sources ADD COLUMN IF NOT EXISTS country TEXT NOT NULL DEFAULT 'INTL';

-- Add country column to jobs
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS country TEXT;

-- Seed Finnish sources
INSERT INTO sources (name, base_url, country) VALUES
    ('duunitori',        'https://duunitori.fi',          'FI'),
    ('jobly',            'https://www.jobly.fi',          'FI'),
    ('tyomarkkinatori',  'https://tyomarkkinatori.fi',    'FI')
ON CONFLICT (name) DO NOTHING;
