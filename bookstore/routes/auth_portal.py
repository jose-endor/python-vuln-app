# RESEARCH: session-based auth, cleartext at rest, weak cookie flags. Not production-safe.
from __future__ import annotations

import os
from typing import Any

from flask import Blueprint, jsonify, request, session

from bookstore.auth_core import check_password, get_user_by_username
from bookstore.sinks.user_mutate_sink import insert_user_raw

bp = Blueprint("auth_portal", __name__)


@bp.route("/api/auth/register", methods=["POST"])
def register() -> Any:
    data = request.get_json(silent=True) or request.form
    u = (data or {}).get("username") or ""
    p = (data or {}).get("password") or ""
    r = (data or {}).get("role") or "user"
    if not u or not p:
        return jsonify({"error": "username and password required"}), 400
    if get_user_by_username(u):
        return jsonify({"error": "username taken"}), 409
    row = {"username": u, "password": p, "role": r}
    uid = insert_user_raw("", row)
    return jsonify({"id": uid, "username": u}), 201


@bp.route("/api/auth/login", methods=["POST"])
def login() -> Any:
    data = request.get_json(silent=True) or request.form
    u = (data or {}).get("username") or ""
    p = (data or {}).get("password") or ""
    rec = get_user_by_username(u)
    if not rec or not check_password(p, str(rec.get("password", ""))):
        return jsonify({"error": "invalid credentials"}), 401
    session["uid"] = int(rec["id"])
    session["username"] = str(rec["username"])
    session["role"] = str(rec.get("role") or "user")
    session.permanent = True
    return jsonify(
        {
            "ok": True,
            "user": {"id": rec["id"], "username": rec["username"], "role": rec.get("role")},
        }
    )


@bp.route("/api/auth/logout", methods=["POST", "GET"])
def logout() -> Any:
    session.clear()
    return jsonify({"ok": True})


@bp.route("/api/auth/me", methods=["GET"])
def me() -> Any:
    if "uid" not in session:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(
        {
            "id": session.get("uid"),
            "username": session.get("username"),
            "role": session.get("role"),
        }
    )


@bp.route("/healthz", methods=["GET"])
@bp.route("/health", methods=["GET"])
def health() -> Any:
    return jsonify(
        {
            "status": "ok",
            "component": os.environ.get("SERVICE_NAME", "api"),
        }
    )
