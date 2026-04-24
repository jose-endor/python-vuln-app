"""POST label — propagates to subprocess shell sink (CWE-78)."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from bookstore.sinks import shell_sink

bp = Blueprint("backup", __name__)


@bp.route("/backup", methods=["POST"])
def backup():
    j = request.get_json(silent=True) or {}
    if isinstance(j, dict) and "label" in j:
        label = j.get("label", "")
    else:
        label = request.form.get("label", "backup")
    return jsonify({"output": shell_sink.run_labeled_command(str(label))})
