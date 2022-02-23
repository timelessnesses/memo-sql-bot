CREATE TABLE IF NOT EXISTS memos(
    id INTEGER,
    text_ TEXT,
    day TEXT,
    when_second INTEGER,
    expires_second INTEGER,
    expire_day TEXT,
    files TEXT,
    author_id INTEGER,
    password TEXT
)