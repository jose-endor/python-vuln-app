from __future__ import annotations

from flask import Blueprint, jsonify, request

from bookstore.services import crypto_utils

bp = Blueprint("curve", __name__)


@bp.route("/curve")
def curve():
    return jsonify({"sample": crypto_utils.describe_curve()})


@bp.route("/seal")
def seal():
    return jsonify({"token": crypto_utils.fernet_seal(request.args.get("q", "preview"))})
