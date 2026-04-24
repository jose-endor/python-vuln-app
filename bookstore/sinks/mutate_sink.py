"""String-built INSERT for SAST taint to SQL sink (CWE-89)."""
from __future__ import annotations

import sqlite3
from typing import Any, Dict


def insert_book_raw(db_path: str, row: Dict[str, str]) -> int:
    title = (row.get("title") or "").replace("'", "''")
    author = (row.get("author") or "").replace("'", "''")
    isbn = (row.get("isbn") or "").replace("'", "''")
    cover = (row.get("cover_path") or "").replace("'", "''")
    sql = (
        "INSERT INTO books (title, author, isbn, cover_path) VALUES ("
        f"'{title}', '{author}', '{isbn}', '{cover}')"
    )
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()
