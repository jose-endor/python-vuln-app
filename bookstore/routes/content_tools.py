"""Publisher-content preview and pattern-review endpoints."""
from __future__ import annotations

from flask import Blueprint, Response, jsonify

from bookstore.access import staff_session
from bookstore.propagation.markdown_chain import chain_markdown_input
from bookstore.propagation.regex_chain import prepare_regex_subject
from bookstore.propagation.xml_chain import normalize_snippet
from bookstore.services import content_format, markup_parse, search_patterns
from bookstore.inputs import content_input

bp = Blueprint("content_tools", __name__)


@bp.route("", methods=["GET"])
@bp.route("/", methods=["GET"])
@staff_session
def operations_index():
    # Provide a concise landing document for authenticated publisher workflows.
    return jsonify(
        {
            "service": "publisher operations",
            "resources": [
                "/ops/content/pattern-review",
                "/ops/content/markdown-preview",
                "/ops/content/fragment-preview",
            ],
        }
    )


@bp.route("/content/pattern-review", methods=["GET", "POST"])
@staff_session
def pattern_review():
    d = content_input.pattern_review_from_request()
    pattern, subject = prepare_regex_subject(str(d.get("pattern", "")), d.get("size", 8000))
    return jsonify(
        {
            "pattern": pattern,
            "subject_len": len(subject),
            "result": search_patterns.match_user_regex(pattern, subject),
        }
    )


@bp.route("/content/markdown-preview", methods=["POST"])
@staff_session
def markdown_preview():
    raw = content_input.text_body()
    html = content_format.render_to_html_chain(chain_markdown_input(raw))
    return Response(html, content_type="text/html; charset=utf-8")


@bp.route("/content/fragment-preview", methods=["POST"])
@staff_session
def fragment_preview():
    raw = content_input.text_body()
    html = markup_parse.serialize_user_fragment(normalize_snippet(raw))
    return Response(html, content_type="text/html; charset=utf-8")
