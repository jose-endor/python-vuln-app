"""Admin preview: template and YAML config ingest helpers."""
from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from bookstore.access import staff_session
from bookstore.propagation import render_pipeline
from bookstore.services import config_parse, template_render
from bookstore.inputs import book_input

bp = Blueprint("preview", __name__)


@bp.route("/preview")
@staff_session
def preview_jacket():
    args = book_input.preview_args()
    body = render_pipeline.pass_through_template(args.get("template", ""))
    return jsonify({"rendered": template_render.render_preview_template(body)})


@bp.route("/ingest", methods=["POST"])
@staff_session
def ingest_publisher_config():
    raw = book_input.config_post()
    cfg = config_parse.materialize_config(raw)
    current_app.config["INGESTED"] = cfg
    return jsonify({"ingested": True, "type": str(type(cfg))})
