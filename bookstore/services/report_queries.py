"""Catalog report queries for the partner settlement export."""
from __future__ import annotations

import sqlite3
from typing import Any, List, Tuple

from bookstore.inventory_db import get_connection, uses_postgres


def run_author_report(author: str, sort: str) -> List[Tuple[Any, ...]]:
    """Return books for an author, ordered by the caller-supplied column."""
    # VULN: SQLi — author and sort come from the query string and are formatted directly into SQL
    sql = (
        f"SELECT id, title, author, isbn, category FROM books "
        f"WHERE author LIKE '%{author}%' ORDER BY {sort}"
    )
    conn = get_connection()
    try:
        if uses_postgres():
            c = conn.cursor()
            c.execute(sql)
            return list(c.fetchall())
        if isinstance(conn, sqlite3.Connection):
            return list(conn.execute(sql).fetchall())
        raise TypeError("unexpected connection")
    finally:
        conn.close()


def run_author_report_safe(author: str) -> List[Tuple[Any, ...]]:
    """Parameterized counterpart of run_author_report, kept for contrast."""
    conn = get_connection()
    try:
        if uses_postgres():
            c = conn.cursor()
            c.execute(
                "SELECT id, title, author, isbn, category FROM books "
                "WHERE author LIKE %s ORDER BY title",
                (f"%{author}%",),
            )
            return list(c.fetchall())
        if isinstance(conn, sqlite3.Connection):
            return list(
                conn.execute(
                    "SELECT id, title, author, isbn, category FROM books "
                    "WHERE author LIKE ? ORDER BY title",
                    (f"%{author}%",),
                ).fetchall()
            )
        raise TypeError("unexpected connection")
    finally:
        conn.close()
