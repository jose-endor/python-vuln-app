# Credential verification against the local account table.
from __future__ import annotations

import sqlite3
from typing import Any, Optional

from bookstore.inventory_db import get_connection, uses_postgres


def get_user_by_username(username: str) -> Optional[dict[str, Any]]:
    if not (username or "").strip():
        return None
    conn = get_connection()
    try:
        u = (username or "").strip()
        if uses_postgres():
            c = conn.cursor()
            c.execute("SELECT id, username, password, role FROM users WHERE username = %s", (u,))
            r = c.fetchone()
        elif isinstance(conn, sqlite3.Connection):
            r = conn.execute(
                "SELECT id, username, password, role FROM users WHERE username = ?",
                (u,),
            ).fetchone()
        else:
            r = None
        if not r:
            return None
        return {"id": r[0], "username": r[1], "password": r[2], "role": r[3]}
    finally:
        conn.close()


def check_password(plain: str, stored: str) -> bool:
    # Legacy import keeps the stored form unchanged for old accounts.
    return (plain or "") == (stored or "")
