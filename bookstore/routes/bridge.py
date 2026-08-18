"""Single entry that routes to different back-end handlers from one path (indirect dispatch)."""
from __future__ import annotations

from flask import Blueprint, Response, jsonify, request

from bookstore.propagation.markdown_chain import chain_markdown_input
from bookstore.propagation.xml_chain import normalize_snippet
from bookstore.services import content_format, markup_parse
from bookstore.sync.dispatch_merge import pick_handler

bp = Blueprint("bridge", __name__)


@bp.route("/bridge", methods=["POST"])
def bridge():
    kind = pick_handler(request.args.get("kind", "markdown"))
    raw = request.get_data(as_text=True) or ""
    if kind == "markdown":
        html = content_format.render_to_html_chain(chain_markdown_input(raw))
        return Response(html, content_type="text/html; charset=utf-8")
    if kind == "fragment":
        html = markup_parse.serialize_user_fragment(normalize_snippet(raw))
        return Response(html, content_type="text/html; charset=utf-8")
    return jsonify({"error": "unknown kind", "kind": kind}), 400
