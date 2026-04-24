"""Run assembled SQL; caller is responsible for parameterization (legacy inventory paths)."""
from __future__ import annotations

import sqlite3
from typing import Any, List, Tuple

from bookstore.inventory_db import get_connection, uses_postgres


def run_list_query(db_path: str, where_sql_fragment: str) -> List[Tuple[Any, ...]]:
    # db_path: legacy param; DSN from DATABASE_URL or INVENTORY_DB_PATH
    _ = db_path
    sql = (
        "SELECT id, title, author, isbn, cover_path, category, summary FROM books WHERE " + where_sql_fragment
    )
    conn = get_connection()
    try:
        if uses_postgres():
            cur = conn.cursor()
            cur.execute(sql)
            return list(cur.fetchall())
        if not isinstance(conn, sqlite3.Connection):
            raise TypeError("unexpected connection type")
        return list(conn.execute(sql).fetchall())
    finally:
        conn.close()
