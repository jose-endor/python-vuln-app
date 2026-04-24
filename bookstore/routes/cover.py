"""Cover file path: propagation -> Pillow (SCA) + path traversal (CWE-22)."""
from __future__ import annotations

import os

from flask import Blueprint, current_app, jsonify, send_file

from bookstore.sinks import pillow_sink
from bookstore.sources import book_input

bp = Blueprint("cover", __name__)


@bp.route("/cover_meta")
def cover_meta():
    base = os.path.join(current_app.root_path, "static", "covers")
    rel = book_input.cover_args().get("path", "default.png")
    return jsonify({"info": pillow_sink.read_cover_meta(base, rel)})


@bp.route("/download_cover")
def download_cover():
    base = os.path.join(current_app.root_path, "static", "covers")
    rel = book_input.cover_args().get("path", "default.png")
    path = os.path.join(base, rel)  # CWE-22: relative paths escape base
    return send_file(path, mimetype="image/png")
