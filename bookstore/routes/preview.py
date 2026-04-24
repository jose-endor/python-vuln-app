"""Admin preview: template propagates to Jinja sink (SSTI)."""
from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from bookstore.propagation import render_pipeline
from bookstore.sinks import jinja_sink, yaml_sink
from bookstore.sources import book_input

bp = Blueprint("preview", __name__)


@bp.route("/preview")
def preview_ssti():
    args = book_input.preview_args()
    body = render_pipeline.pass_through_template(args.get("template", ""))
    return jsonify({"rendered": jinja_sink.render_unsafe(body)})


@bp.route("/ingest", methods=["POST"])
def ingest_yaml_config():
    raw = book_input.config_post()
    cfg = yaml_sink.materialize_config(raw)
    current_app.config["INGESTED"] = cfg
    return jsonify({"ingested": True, "type": str(type(cfg))})
