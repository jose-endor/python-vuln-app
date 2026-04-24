"""SQL execution sink (SAST: sink — CWE-89)."""
from __future__ import annotations

import sqlite3
from typing import Any, List, Tuple


def run_list_query(db_path: str, where_sql_fragment: str) -> List[Tuple[Any, ...]]:
    conn = sqlite3.connect(db_path)
    try:
        sql = "SELECT id, title, author, isbn, cover_path FROM books WHERE " + where_sql_fragment
        return list(conn.execute(sql).fetchall())
    finally:
        conn.close()
