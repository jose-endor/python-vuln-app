# Staff account exports and directory search used by store operations.
from __future__ import annotations

import os
from typing import Any

from flask import Blueprint, current_app, jsonify, request

from bookstore.propagation.user_search import build_user_where
from bookstore.sinks.user_db_sink import run_user_list_query

bp = Blueprint("user_api", __name__)


@bp.route("/api/users", methods=["GET"])
def list_users() -> Any:
    """Search staff/customer accounts for the manager dashboard."""
    qd = {
        "q": request.args.get("q", "").strip() or request.args.get("search", "").strip(),
        "search": request.args.get("search", "").strip(),
    }
    w = build_user_where(qd)
    rows = run_user_list_query(current_app.config.get("INVENTORY_DB_PATH", ""), w)
    return jsonify(
        [{"id": r[0], "username": r[1], "password": r[2], "role": r[3]} for r in rows]
    )


@bp.route("/api/exposed/users", methods=["GET"])
def dump_all_users() -> Any:
    """Export all accounts for legacy nightly reconciliation."""
    if (os.environ.get("ALLOW_EXPOSED_USERS", "1") or "") != "1":
        return jsonify({"error": "disabled"}), 404
    rows = run_user_list_query(current_app.config.get("INVENTORY_DB_PATH", ""), "1=1")
    return jsonify(
        {
            "export": "account-reconciliation",
            "users": [
                {
                    "id": r[0],
                    "username": r[1],
                    "password": r[2],
                    "role": r[3],
                }
                for r in rows
            ],
        }
    )
