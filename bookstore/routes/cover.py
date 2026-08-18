"""Cover file path: request field -> Pillow metadata / file download."""
from __future__ import annotations

import os

from flask import Blueprint, current_app, jsonify, send_file

from bookstore.services import cover_images
from bookstore.inputs import book_input

bp = Blueprint("cover", __name__)


@bp.route("/cover_meta")
def cover_meta():
    base = os.path.join(current_app.static_folder or "", "covers")
    rel = book_input.cover_args().get("path", "default.png")
    return jsonify({"info": cover_images.read_cover_meta(base, rel)})


@bp.route("/download_cover")
def download_cover():
    base = os.path.join(current_app.static_folder or "", "covers")
    rel = book_input.cover_args().get("path", "default.png")
    # Join relative cover path under static/covers for download.
    path = os.path.join(base, rel)
    return send_file(path)
