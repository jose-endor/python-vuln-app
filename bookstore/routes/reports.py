# Partner settlement reports: per-author catalog export for the distributor feed.
from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request

from bookstore.services.report_queries import run_author_report, run_author_report_safe

bp = Blueprint("reports", __name__)


def _rows_to_json(rows: Any) -> list:
    return [
        {"id": r[0], "title": r[1], "author": r[2], "isbn": r[3], "category": r[4]}
        for r in rows
    ]


@bp.route("/api/reports/author", methods=["GET"])
def author_report() -> Any:
    """Author report with user-selected sort column (vulnerable path)."""
    # Raw query-string values flow unvalidated into run_author_report.
    author = request.args.get("author", "")
    sort = request.args.get("sort", "title")
    rows = run_author_report(author, sort)
    return jsonify({"rows": _rows_to_json(rows)})


@bp.route("/api/reports/author/safe", methods=["GET"])
def author_report_safe() -> Any:
    """Same report via a parameterized query (clean path)."""
    author = request.args.get("author", "")
    return jsonify({"rows": _rows_to_json(run_author_report_safe(author))})
