import os
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  isbn TEXT,
  cover_path TEXT
);
"""


def init_db(db_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(db_path)) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM books")
        if cur.fetchone()[0] == 0:
            samples = [
                ("The Phish of The Ring", "J.R. Token", "111-1", "static/covers/default.png"),
                ("A SQL of Ice and Fire", "George R. DROP TABLE", "222-2", "static/covers/default.png"),
            ]
            conn.executemany(
                "INSERT INTO books (title, author, isbn, cover_path) VALUES (?, ?, ?, ?)", samples
            )
            conn.commit()
    finally:
        conn.close()
