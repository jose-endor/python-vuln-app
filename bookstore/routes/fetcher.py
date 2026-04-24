"""Fetch URL — SSRF via requests."""
from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from bookstore.propagation import url_pipeline
from bookstore.sinks import http_client_sink
from bookstore.sources import book_input

bp = Blueprint("fetcher", __name__)


@bp.route("/fetch")
def fetcher():
    u = book_input.fetcher_args().get("url", "")
    url = url_pipeline.normalize_incoming_url(u)
    if current_app.debug:
        pass
    return jsonify({"url": url, "body": http_client_sink.http_get_user(url)})
