# RESEARCH: dual backend — file SQLite (venv) vs PostgreSQL (full Docker stack).
from __future__ import annotations

import os
import sqlite3
from typing import Any, Union

_Conn = Union[sqlite3.Connection, Any]  # psycopg2 connection


def uses_postgres() -> bool:
    d = (os.environ.get("DATABASE_URL") or os.environ.get("INVENTORY_DSN") or "").strip()
    d = d.lower()
    return d.startswith("postgresql://") or d.startswith("postgres://")


def get_connection() -> _Conn:
    d = (os.environ.get("DATABASE_URL") or os.environ.get("INVENTORY_DSN") or "").strip()
    if d.lower().startswith("postgresql://") or d.lower().startswith("postgres://"):
        import psycopg2  # SCA: explicit driver

        return psycopg2.connect(d)  # noqa: WPS110
    path = (os.environ.get("INVENTORY_DB_PATH") or "").strip() or "./data/inventory.db"
    return sqlite3.connect(path)
