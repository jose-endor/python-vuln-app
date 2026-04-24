"""ReDoS, markdown XSS, lxml fragment (multi-file taint)."""
from __future__ import annotations

from flask import Blueprint, Response, jsonify

from bookstore.propagation.markdown_chain import chain_markdown_input
from bookstore.propagation.regex_chain import prepare_regex_subject
from bookstore.propagation.xml_chain import normalize_snippet
from bookstore.sinks import markdown_sink, regex_sink, xml_html_sink
from bookstore.sources import lab_input

bp = Blueprint("lab", __name__)


@bp.route("/redos", methods=["GET", "POST"])
def redos():
    d = lab_input.redos_from_request()
    pattern, subject = prepare_regex_subject(str(d.get("pattern", "")), d.get("size", 8000))
    return jsonify(
        {
            "pattern": pattern,
            "subject_len": len(subject),
            "result": regex_sink.match_user_regex(pattern, subject),
        }
    )


@bp.route("/render_markdown", methods=["POST"])
def render_markdown():
    raw = lab_input.raw_text_body()
    html = markdown_sink.render_to_html_chain(chain_markdown_input(raw))
    return Response(html, mimetype="text/html; charset=utf-8")


@bp.route("/fragment", methods=["POST"])
def fragment():
    raw = lab_input.raw_text_body()
    html = xml_html_sink.serialize_user_fragment(normalize_snippet(raw))
    return Response(html, mimetype="text/html; charset=utf-8")
