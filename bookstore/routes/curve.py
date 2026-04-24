from __future__ import annotations

from flask import Blueprint, jsonify, request

from bookstore.sinks import crypto_sink

bp = Blueprint("curve", __name__)


@bp.route("/curve")
def curve():
    return jsonify({"sample": crypto_sink.describe_curve()})


@bp.route("/seal")
def seal():
    return jsonify({"token": crypto_sink.fernet_seal(request.args.get("q", "demo"))})
