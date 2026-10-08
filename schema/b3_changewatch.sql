-- 👀 changewatch schema
CREATE TABLE watches(id INTEGER PRIMARY KEY, url TEXT, selector TEXT, interval INTEGER DEFAULT 3600, ignore_pattern TEXT, alert_url TEXT, last_hash TEXT, last_checked DATETIME, created_at DATETIME);
CREATE TABLE snapshots(id INTEGER PRIMARY KEY, watch_id INTEGER REFERENCES watches(id), content TEXT, hash TEXT, at DATETIME);
