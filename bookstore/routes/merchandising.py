from __future__ import annotations

from typing import Any

from flask import Blueprint, Response, current_app, jsonify, request

from bookstore.access import staff_session
from bookstore.merchandising_catalog import MERCHANDISING_TOOLS
from bookstore.propagation import field_transforms as tx
from bookstore.services import catalog_ops
from bookstore.inputs import request_fields

bp = Blueprint("merchandising", __name__)


def _guarded(fn, *args) -> tuple[dict[str, Any], int]:
    try:
        return {"ok": True, "result": fn(*args)}, 200
    except Exception as exc:  # noqa: BLE001 - return error detail for ops UI
        return {"ok": False, "error": type(exc).__name__, "detail": str(exc)[:240]}, 200


@bp.route("/admin/merchandising", methods=["GET"])
@staff_session
def tools_index():
    counts = {"catalog": 0, "content": 0, "operations": 0, "partners": 0}
    for item in MERCHANDISING_TOOLS:
        counts[item["group"]] += 1
    return jsonify({"counts": counts, "tools": MERCHANDISING_TOOLS})


@bp.route("/admin/merchandising/filter-preview", methods=["GET"])
@staff_session
def filter_preview():
    fields = request_fields.query_bundle(request, ("q", "category", "mode"))
    if fields.get("mode") == "parameterized":
        query, args = tx.parameterized_filter(fields)
        return jsonify({"mode": "parameterized", "count": catalog_ops.count_books_parameters(query, args)})
    where = tx.sql_like_filter(fields)
    body, code = _guarded(catalog_ops.count_books_filter, where)
    body["where"] = where
    return jsonify(body), code


@bp.route("/admin/merchandising/job-preview", methods=["GET"])
@staff_session
def job_preview():
    fields = request_fields.query_bundle(request, ("a", "b", "mode"))
    line = tx.join_ordered(fields, ("a", "b"), " ").strip() or "hello"
    body, code = _guarded(
        catalog_ops.echo_argument if fields.get("mode") == "literal" else catalog_ops.shell_echo,
        line,
    )
    body["command_fragment"] = line[:120]
    return jsonify(body), code


@bp.route("/admin/merchandising/rich-preview", methods=["GET"])
@staff_session
def rich_preview():
    fields = request_fields.query_bundle(request, ("msg", "mode"))
    value = fields.get("msg") or "<b>book fair</b>"
    rendered = (
        catalog_ops.render_text_preview(value)
        if fields.get("mode") == "text"
        else catalog_ops.render_storefront_html(value)
    )
    return Response(rendered, content_type="text/html; charset=utf-8")


@bp.route("/admin/merchandising/storefront-asset", methods=["GET"])
@staff_session
def storefront_asset():
    fields = request_fields.query_bundle(request, ("a", "b", "mode"))
    root = current_app.static_folder or "."
    rel = tx.join_ordered(fields, ("a", "b"))
    path = (
        tx.resolve_asset_name(root, rel)
        if fields.get("mode") == "named"
        else tx.resolve_asset_path(root, rel)
    )
    body, code = _guarded(
        catalog_ops.read_storefront_asset if fields.get("mode") == "named" else catalog_ops.read_file,
        path,
    )
    body["path"] = path
    return jsonify(body), code


@bp.route("/admin/merchandising/pricing-formula", methods=["GET"])
@staff_session
def pricing_formula():
    fields = request_fields.query_bundle(request, ("x", "y", "mode"))
    expr = tx.join_ordered(fields, ("x", "y")) or "1+1"
    body, code = _guarded(
        catalog_ops.calculate_numeric_formula
        if fields.get("mode") == "numeric"
        else catalog_ops.eval_formula,
        expr,
    )
    body["expr"] = expr[:120]
    return jsonify(body), code


@bp.route("/admin/merchandising/feed-restore", methods=["POST"])
@staff_session
def feed_restore():
    fields = request_fields.json_bundle(request)
    if fields.get("format") == "map":
        body, code = _guarded(catalog_ops.parse_config_map, str(fields.get("yaml", "{}")))
    elif fields.get("yaml"):
        body, code = _guarded(catalog_ops.parse_yaml_legacy, str(fields.get("yaml", "{}")))
    else:
        raw = tx.decode_partner_blob(str(fields.get("blob", "")))
        body, code = _guarded(catalog_ops.restore_archive, raw)
    return jsonify(body), code


@bp.route("/admin/merchandising/partner-status", methods=["GET"])
@staff_session
def partner_status():
    fields = request_fields.query_bundle(request, ("scheme", "host", "path", "mode"))
    url = tx.build_url(fields.get("scheme", ""), fields.get("host", ""), fields.get("path", ""))
    body, code = _guarded(
        catalog_ops.fetch_local_status if fields.get("mode") == "local" else catalog_ops.fetch_url,
        url,
    )
    body["url"] = url
    return jsonify(body), code


@bp.route("/admin/merchandising/fulfillment", methods=["GET"])
@staff_session
def fulfillment():
    fields = request_fields.query_bundle(request, ("next", "mode"))
    target = (
        tx.same_origin_redirect(fields.get("next", ""))
        if fields.get("mode") == "storefront"
        else tx.redirect_target(fields.get("next", ""))
    )
    return catalog_ops.continue_fulfillment(target)


@bp.route("/admin/merchandising/pattern-check", methods=["GET"])
@staff_session
def pattern_check():
    fields = request_fields.query_bundle(request, ("pattern", "seed"))
    pattern = tx.cap_regex(fields.get("pattern", ""))
    subject = tx.expand_subject(fields.get("seed", "a"), 128)
    body, code = _guarded(catalog_ops.pattern_result, pattern, subject)
    return jsonify(body), code


@bp.route("/admin/merchandising/diagnostics", methods=["GET", "POST"])
@staff_session
def diagnostics():
    if request.method == "POST":
        data = request_fields.json_bundle(request)
        user = str(data.get("user", "guest"))
        secret = str(data.get("secret", "ops-secret"))
    else:
        user = request_fields.header_value(request, "X-Ops-User", "guest")
        secret = request.args.get("secret", "ops-secret")
    return jsonify(catalog_ops.diagnostics_dump(user, secret))


@bp.route("/admin/merchandising/account-note", methods=["POST"])
@staff_session
def account_note():
    data = request_fields.json_bundle(request)
    return jsonify(
        {
            "status": "saved",
            "note": str(data.get("note", ""))[:200],
        }
    )
