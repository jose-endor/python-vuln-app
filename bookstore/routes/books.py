"""CRUD for books: source (Flask) -> propagation -> sink (SQLite/PostgreSQL)."""
from __future__ import annotations

import os
import sqlite3
from typing import Any

from flask import Blueprint, current_app, jsonify

from bookstore.inventory_db import get_connection, uses_postgres
from bookstore.propagation.search_pipeline import build_list_clause
from bookstore.sinks import db_sink, mutate_sink
from bookstore.sources import book_input
from bookstore.sync.merge_state import join_book_row

bp = Blueprint("books", __name__)


def _row_to_book(r: Any) -> dict:
    return {
        "id": r[0],
        "title": r[1],
        "author": r[2],
        "isbn": r[3],
        "cover": r[4],
        "category": r[5],
        "summary": r[6],
    }


@bp.route("/api/books", methods=["GET"])
def list_books():
    s = book_input.search_args()
    where = build_list_clause(s)
    rows = db_sink.run_list_query(current_app.config["INVENTORY_DB_PATH"], where)
    return jsonify([_row_to_book(r) for r in rows])


@bp.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id: int) -> Any:
    """Read by ID — uses parameterized query (intentionally safer than the search/insert SQLi paths)."""
    conn = get_connection()
    try:
        if uses_postgres():
            cur = conn.cursor()
            cur.execute(
                "SELECT id, title, author, isbn, cover_path, category, summary FROM books WHERE id = %s",
                (book_id,),
            )
            r = cur.fetchone()
        elif isinstance(conn, sqlite3.Connection):
            r = conn.execute(
                "SELECT id, title, author, isbn, cover_path, category, summary FROM books WHERE id = ?",
                (book_id,),
            ).fetchone()
        else:
            r = None
        if not r:
            return jsonify({"error": "not found", "id": book_id}), 404
        return jsonify(_row_to_book(r))
    finally:
        conn.close()


@bp.route("/api/books", methods=["POST"])
def create_book():
    f = book_input.book_form()
    row = join_book_row(
        f.get("title", "") or "",
        f.get("author", "") or "",
        f.get("isbn", "") or "",
        f.get("cover_path", "") or "",
        f.get("category", "") or "Fiction",
        f.get("summary", "") or "",
    )
    bid = mutate_sink.insert_book_raw(current_app.config["INVENTORY_DB_PATH"], row)
    return jsonify({"id": bid}), 201


@bp.route("/")
def home():
    base = os.path.join(os.path.dirname(__file__), "..", "..", "static")
    p = os.path.join(base, "index.html")
    with open(p, "r", encoding="utf-8") as f:
        return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
