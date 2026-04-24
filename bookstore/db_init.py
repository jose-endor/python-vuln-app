import os
import sqlite3
from typing import Any

# RESEARCH: sample inventory for a believable small bookstore UI; paths are under /static
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


def _seed_books() -> list[tuple[str, str, str, str, str, str]]:
    c = "covers/default.png"
    return [
        (
            "The Nightingale",
            "Kristin Hannah",
            "978-0-31-234454-2",
            c,
            "Fiction",
            "Two sisters in German-occupied France and the choices that shape their lives — staff pick for book clubs.",
        ),
        (
            "Project Hail Mary",
            "Andy Weir",
            "978-0-59-313520-4",
            c,
            "Science Fiction",
            "A lone astronaut races to save Earth with humor, science, and heart; great for long flights.",
        ),
        (
            "Dune",
            "Frank Herbert",
            "978-0-44-101359-3",
            c,
            "Science Fiction",
            "Political intrigue, ecology, and destiny on a desert world — a genre-defining classic.",
        ),
        (
            "The Pragmatic Programmer",
            "David Thomas, Andrew Hunt",
            "978-0-13-475759-9",
            c,
            "Software",
            "Timeless advice on craft, DRY, tracer bullets, and shipping maintainable code.",
        ),
        (
            "Security Engineering (3rd ed.)",
            "Ross Anderson",
            "978-1-19-124332-0",
            c,
            "Security",
            "How real systems fail and how to design them to be robust — a practitioner's reference.",
        ),
        (
            "SQL Antipatterns",
            "Bill Karwin",
            "978-1-93-435655-1",
            c,
            "Database",
            "A catalog of database mistakes (and safer patterns) — ironically well paired with our SQLi demos.",
        ),
        (
            "The Phish of the Ring (spoof)",
            "J.R. Token",
            "111-000-000-001",
            c,
            "Parody / Research",
            "A tongue-in-cheek title kept for **AppSec** regression demos. Not a real print edition.",
        ),
        (
            "A SQL of Ice and Fire (demo)",
            "George R. DROP TABLE",
            "111-000-000-002",
            c,
            "Parody / Research",
            "Fictional catalog entry for **CWE-89** lab traces — the pun is the payload.",
        ),
        (
            "The Mythical Man-Month",
            "Frederick P. Brooks Jr.",
            "978-0-20-183595-3",
            c,
            "Software",
            "Essays on software project management — “adding people to a late project makes it later.”",
        ),
        (
            "Clean Code",
            "Robert C. Martin",
            "978-0-13-235088-4",
            c,
            "Software",
            "Naming, functions, error handling, and the habits that make code easy to change.",
        ),
        (
            "1984",
            "George Orwell",
            "978-0-45-152493-5",
            c,
            "Fiction",
            "Dystopian surveillance and truth — a frequent classroom assignment worldwide.",
        ),
        (
            "Sapiens",
            "Yuval Noah Harari",
            "978-0-06-231610-3",
            c,
            "History",
            "A fast-paced history of humankind from the cognitive revolution to today.",
        ),
        (
            "The Rust Programming Language (online)",
            "Steve Klabnik, Carol Nichols",
            "978-0-00-000000-0",
            c,
            "Software",
            "The canonical book on memory-safe systems programming; cover image is a placeholder in this shop.",
        ),
        (
            "The Thursday Murder Club",
            "Richard Osman",
            "978-0-25-300060-0",
            c,
            "Mystery",
            "Retirement-home sleuths, cozy Brit wit, and clever plotting — a bestseller for a reason.",
        ),
        (
            "Atomic Habits",
            "James Clear",
            "978-0-73-521129-2",
            c,
            "Nonfiction",
            "Small, repeatable changes that shape identity — we stock this next to the programming aisle.",
        ),
        (
            "The DevOps Handbook",
            "Gene Kim, et al.",
            "978-1-94-104800-0",
            c,
            "Software",
            "CAMS, the three ways, and what high-performing technology organizations have in common.",
        ),
        (
            "Pride and Prejudice",
            "Jane Austen",
            "978-0-14-143951-8",
            c,
            "Classics",
            "Romance, manners, and Elizabeth Bennet—perennial fiction floor staple.",
        ),
        (
            "Meditations",
            "Marcus Aurelius (Gregory Hays trans.)",
            "978-0-81-296358-5",
            c,
            "Philosophy",
            "Stoic journals from a Roman emperor — short chapters for the commute.",
        ),
    ]


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


def _seed_users() -> list[tuple[str, str, str]]:
    # RESEARCH: cleartext passwords in DB (CWE-256 / CWE-916 class signals for scanners)
    return [
        ("admin", "admin", "admin"),
        ("demo", "demo", "user"),
    ]


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
                _seed_books(),
            )
        cur.execute("SELECT COUNT(*) FROM users")
        nu = int(cur.fetchone()[0] or 0)
        if nu == 0:
            cur.executemany("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", _seed_users())
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
                _seed_books(),
            )
        cur2 = conn.cursor()
        cur2.execute("SELECT COUNT(*) FROM users")
        if int(cur2.fetchone()[0] or 0) == 0:
            conn.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", _seed_users())
        conn.commit()
    finally:
        conn.close()
