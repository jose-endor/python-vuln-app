"""Bulk / batch INSERT with operator-provided string fragments (catalog intake)."""
from __future__ import annotations

import sqlite3
from typing import Any, Dict

from bookstore.inventory_db import get_connection, uses_postgres


def insert_book_raw(db_path: str, row: Dict[str, str]) -> int:
    # db_path: legacy; connection from env (see inventory_db)
    _ = db_path
    title = (row.get("title") or "").replace("'", "''")
    author = (row.get("author") or "").replace("'", "''")
    isbn = (row.get("isbn") or "").replace("'", "''")
    cover = (row.get("cover_path") or "").replace("'", "''")
    category = (row.get("category") or "Fiction").replace("'", "''")
    summary = (row.get("summary") or "").replace("'", "''")
    pg = uses_postgres()
    if pg:
        sql = (
            "INSERT INTO books (title, author, isbn, cover_path, category, summary) VALUES ("
            f"'{title}', '{author}', '{isbn}', '{cover}', '{category}', '{summary}') RETURNING id"
        )
    else:
        sql = (
            "INSERT INTO books (title, author, isbn, cover_path, category, summary) VALUES ("
            f"'{title}', '{author}', '{isbn}', '{cover}', '{category}', '{summary}')"
        )
    conn = get_connection()
    try:
        cur: Any
        if pg:
            cur = conn.cursor()
            cur.execute(sql)
            r = cur.fetchone()
            conn.commit()
            return int(r[0]) if r else 0
        if isinstance(conn, sqlite3.Connection):
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            return int(cur.lastrowid)
        raise TypeError("unexpected connection type")
    finally:
        conn.close()
