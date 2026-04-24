"""CRUD for books: source (Flask) -> propagation -> sink (SQLite)."""
from __future__ import annotations

import os

from flask import Blueprint, current_app, jsonify

from bookstore.propagation.search_pipeline import build_list_clause
from bookstore.sinks import db_sink, mutate_sink
from bookstore.sources import book_input
from bookstore.sync.merge_state import join_book_row

bp = Blueprint("books", __name__)


@bp.route("/api/books", methods=["GET"])
def list_books():
    s = book_input.search_args()
    where = build_list_clause(s)
    rows = db_sink.run_list_query(current_app.config["INVENTORY_DB_PATH"], where)
    return jsonify([{"id": r[0], "title": r[1], "author": r[2], "isbn": r[3], "cover": r[4]} for r in rows])


@bp.route("/api/books", methods=["POST"])
def create_book():
    f = book_input.book_form()
    row = join_book_row(
        (f.get("title", ""), f.get("author", ""), f.get("isbn", ""), f.get("cover_path", ""))
    )
    bid = mutate_sink.insert_book_raw(current_app.config["INVENTORY_DB_PATH"], row)
    return jsonify({"id": bid}), 201


@bp.route("/")
def home():
    base = os.path.join(os.path.dirname(__file__), "..", "..", "static")
    p = os.path.join(base, "index.html")
    with open(p, "r", encoding="utf-8") as f:
        return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
