"""POST label — runs a labeled backup job via subprocess."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from bookstore.services import backup_jobs

bp = Blueprint("backup", __name__)


@bp.route("/backup", methods=["POST"])
def backup():
    j = request.get_json(silent=True) or {}
    if isinstance(j, dict) and "label" in j:
        label = j.get("label", "")
    else:
        label = request.form.get("label", "backup")
    return jsonify({"output": backup_jobs.run_labeled_command(str(label))})
