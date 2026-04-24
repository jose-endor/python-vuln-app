import os
import sqlite3
from typing import Any

from bookstore.seed_data import load_book_seed_rows, load_user_seed_rows

# Books & accounts: first import from `data/inventory.json` + `data/users.json` (see seed_data).
SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  isbn TEXT,
  cover_path TEXT,
  category TEXT NOT NULL DEFAULT 'Fiction',
  summary TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user'
);
"""


def _ensure_columns(conn: sqlite3.Connection) -> None:
    cur = conn.execute("PRAGMA table_info(books)")
    col_names = {str(row[1]) for row in cur.fetchall()}
    if "category" not in col_names:
        conn.execute("ALTER TABLE books ADD COLUMN category TEXT NOT NULL DEFAULT 'Fiction'")
    if "summary" not in col_names:
        conn.execute("ALTER TABLE books ADD COLUMN summary TEXT NOT NULL DEFAULT ''")
    conn.commit()


def _ensure_users_table(conn: sqlite3.Connection) -> None:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cur.fetchone() is None:
        conn.execute(
            """CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user'
)"""
        )
    conn.commit()


PG_SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  isbn TEXT,
  cover_path TEXT,
  category TEXT NOT NULL DEFAULT 'Fiction',
  summary TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user'
);
"""


def _init_postgres() -> None:
    import psycopg2  # SCA: driver in use when DATABASE_URL is set (Docker)

    dsn = (os.environ.get("DATABASE_URL") or os.environ.get("INVENTORY_DSN") or "").strip()
    conn: Any = psycopg2.connect(dsn)
    try:
        cur = conn.cursor()
        cur.execute(PG_SCHEMA)
        cur.execute("SELECT COUNT(*) FROM books")
        n = int(cur.fetchone()[0] or 0)
        if n == 0:
            cur.executemany(
                "INSERT INTO books (title, author, isbn, cover_path, category, summary) VALUES (%s, %s, %s, %s, %s, %s)",
                load_book_seed_rows(),
            )
        cur.execute("SELECT COUNT(*) FROM users")
        nu = int(cur.fetchone()[0] or 0)
        if nu == 0:
            cur.executemany(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", load_user_seed_rows()
            )
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: str) -> None:
    d = (os.environ.get("DATABASE_URL") or os.environ.get("INVENTORY_DSN") or "").strip()
    if d.lower().startswith("postgresql://") or d.lower().startswith("postgres://"):
        _init_postgres()
        return
    os.makedirs(os.path.dirname(os.path.abspath(db_path)) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        _ensure_columns(conn)
        _ensure_users_table(conn)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM books")
        if cur.fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO books (title, author, isbn, cover_path, category, summary) VALUES (?, ?, ?, ?, ?, ?)",
                load_book_seed_rows(),
            )
        cur2 = conn.cursor()
        cur2.execute("SELECT COUNT(*) FROM users")
        if int(cur2.fetchone()[0] or 0) == 0:
            conn.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", load_user_seed_rows())
        conn.commit()
    finally:
        conn.close()
