"""Vulnerable list query on users (CWE-89) — SAST: distinct sink from book list."""
from __future__ import annotations

import sqlite3
from typing import Any, List, Tuple

from bookstore.inventory_db import get_connection, uses_postgres


def run_user_list_query(_db_path: str, where_sql_fragment: str) -> List[Tuple[Any, ...]]:
    _ = _db_path
    sql = "SELECT id, username, password, role FROM users WHERE " + where_sql_fragment
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
