# RESEARCH: string-built INSERT for user registration (CWE-89) — same class as book insert.
from __future__ import annotations

import sqlite3
from typing import Any, Dict

from bookstore.inventory_db import get_connection, uses_postgres


def insert_user_raw(_db_path: str, row: Dict[str, str]) -> int:
    u = (row.get("username") or "").replace("'", "''")
    p = (row.get("password") or "").replace("'", "''")
    r = (row.get("role") or "user").replace("'", "''")
    pg = uses_postgres()
    if pg:
        sql = f"INSERT INTO users (username, password, role) VALUES ('{u}', '{p}', '{r}') RETURNING id"
    else:
        sql = f"INSERT INTO users (username, password, role) VALUES ('{u}', '{p}', '{r}')"
    conn = get_connection()
    try:
        if pg:
            c = conn.cursor()
            c.execute(sql)
            rowi = c.fetchone()
            conn.commit()
            return int(rowi[0]) if rowi else 0
        if isinstance(conn, sqlite3.Connection):
            c2 = conn.cursor()
            c2.execute(sql)
            conn.commit()
            return int(c2.lastrowid)
        raise TypeError("unexpected connection")
    finally:
        conn.close()
