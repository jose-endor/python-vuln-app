"""Single entry that routes to different sinks (indirect call — harder for some SAST)."""
from __future__ import annotations

from flask import Blueprint, Response, jsonify, request

from bookstore.propagation.markdown_chain import chain_markdown_input
from bookstore.propagation.xml_chain import normalize_snippet
from bookstore.sinks import markdown_sink, xml_html_sink
from bookstore.sync.dispatch_merge import pick_handler

bp = Blueprint("bridge", __name__)


@bp.route("/bridge", methods=["POST"])
def bridge():
    kind = pick_handler(request.args.get("kind", "markdown"))
    raw = request.get_data(as_text=True) or ""
    if kind == "markdown":
        html = markdown_sink.render_to_html_chain(chain_markdown_input(raw))
        return Response(html, mimetype="text/html; charset=utf-8")
    if kind == "fragment":
        html = xml_html_sink.serialize_user_fragment(normalize_snippet(raw))
        return Response(html, mimetype="text/html; charset=utf-8")
    return jsonify({"error": "unknown kind", "kind": kind}), 400
