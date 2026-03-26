INSERT INTO sources (name, base_url, country) VALUES
    ('linkedin', 'https://www.linkedin.com/jobs', 'INTL')
ON CONFLICT (name) DO NOTHING;
