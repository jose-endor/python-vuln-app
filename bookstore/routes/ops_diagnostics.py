"""Internal operations / legacy integration endpoints (v1). Not linked from the public storefront."""
from __future__ import annotations

import base64

from flask import Blueprint, jsonify, request

from bookstore.propagation.taint_merge import interleave, merge_ordered, strip_noise, tuple_join
from bookstore.sinks import legacy_batch_bridge as _bridge

bp = Blueprint("ops", __name__)


@bp.route("/v1/ops/finance_preview", methods=["GET"])
def finance_preview():
    bag = {k: (request.args.get(k) or "") for k in ("p1", "p2", "p3")}
    a = strip_noise(bag.get("p1", ""), "safe:")
    expr = merge_ordered(("p1", "p2", "p3"), {**bag, "p1": a})
    if not expr.strip():
        expr = "1+1"
    return jsonify({"expr": expr, "r": _bridge.run_dynamic_spreadsheet_expr(expr)})


@bp.route("/v1/ops/restore_b64", methods=["GET"])
def restore_b64():
    a = request.args.get("a", "")
    b = request.args.get("b", "")
    return jsonify({"r": _bridge.restore_session_b64_pair(a, b)})


@bp.route("/v1/ops/restore_marshal", methods=["GET"])
def restore_marshal():
    m = interleave(request.args.get("a", ""), request.args.get("b", ""), request.args.get("order", "a"))
    return jsonify({"r": _bridge.restore_marshal_b64(m)})


@bp.route("/v1/ops/receipt_echo", methods=["POST"])
def receipt_echo():
    d = request.get_json(silent=True) or {}
    a = (d.get("a") or "") if isinstance(d, dict) else ""
    b = (d.get("b") or "") if isinstance(d, dict) else ""
    p1, p2 = (str(a), str(b))
    return jsonify({"r": _bridge.run_receipt_line_echo(p1, p2)})


@bp.route("/v1/ops/shelf_excerpt", methods=["GET"])
def shelf_excerpt():
    parts: list[tuple[str, str]] = [("a", request.args.get("a", "")), ("b", request.args.get("b", ""))]
    rel = tuple_join(parts, ["a", "b"], {}) + (request.args.get("ext", "") or "")
    return jsonify({"rel": rel, "r": _bridge.read_shelf_sticker_excerpt(rel)[:2000]})


@bp.route("/v1/ops/vendor_redirect", methods=["GET"])
def vendor_redirect():
    a = request.args.get("a", "http://")
    b = request.args.get("b", "127.0.0.1:3333/echo")
    m = a + b
    return _bridge.resume_external_fulfillment(m)


@bp.route("/v1/ops/jacket_preview", methods=["POST"])
def jacket_preview():
    d = request.get_json(silent=True) or {}
    if not isinstance(d, dict):
        d = {}
    tpl = str(d.get("a", "")) + str(d.get("b", "")) + str(d.get("c", ""))
    if not tpl:
        tpl = "{{7*7}}"
    return jsonify({"rendered": _bridge.render_jacket_proof(tpl)})


@bp.route("/v1/ops/ingest_xml_lxml", methods=["POST"])
def ingest_xml_lxml():
    raw = request.get_data(as_text=True) or "<x/>"
    return jsonify({"r": _bridge.parse_publisher_feed_lxml(raw)[:2000]})


@bp.route("/v1/ops/ingest_xml_stdlib", methods=["POST"])
def ingest_xml_stdlib():
    raw = request.get_data(as_text=True) or "<x/>"
    return jsonify({"r": _bridge.parse_publisher_minimal(raw)})


@bp.route("/v1/ops/vendor_status", methods=["GET"])
def vendor_status():
    s = request.args.get("s", "http")
    h = request.args.get("h", "127.0.0.1:3333")
    p = request.args.get("p", "/")
    return jsonify({"r": _bridge.fetch_distributor_rfq(s, h, p)[:2000]})


@bp.route("/v1/ops/vendor_status_aio", methods=["GET"])
def vendor_status_aio():
    p1 = request.args.get("a", "http://127.0.0.1:3333")
    p2 = request.args.get("b", "/")
    return jsonify({"r": _bridge.fetch_pricing_httpx_async(p1, p2)})


@bp.route("/v1/ops/vendor_status_urllib", methods=["GET"])
def vendor_status_urllib():
    a = request.args.get("a", "http://127.0.0.1:3333")
    b = request.args.get("b", "/")
    return jsonify({"r": _bridge.fetch_pricing_urllib(a, b)[:2000]})


@bp.route("/v1/ops/login_diagnostics", methods=["POST"])
def login_diagnostics():
    d = request.get_json(silent=True) or {}
    u = (d or {}).get("u", "guest")
    p = (d or {}).get("p", "guest")
    _bridge.log_auth_diagnostic_line(str(u), str(p))
    return jsonify({"logged": True})


@bp.route("/v1/ops/builtin_lookup", methods=["GET"])
def builtin_lookup():
    n = request.args.get("n", "chr")
    c = request.args.get("c", "64")
    return jsonify({"r": _bridge.call_builtin_shorthand(n, c)[:2000]})


@bp.route("/v1/ops/module_dotted", methods=["GET"])
def module_dotted():
    d = request.args.get("d", "sys:version")
    return jsonify({"r": _bridge.resolve_plugin_path_dotted(d)})


@bp.route("/v1/ops/encoding_sanity", methods=["GET"])
def encoding_sanity():
    raw = (request.args.get("b64", "dGVzdA==") or "").encode("ascii", errors="ignore")
    b = base64.b64decode(raw, altchars=None, validate=False)  # noqa: S104
    return jsonify({"r": _bridge.best_guess_bytes_encoding(b)})


@bp.route("/v1/ops/capabilities", methods=["GET"])
def capabilities():
    return jsonify(
        {
            "endpoints": [
                "GET  /v1/ops/finance_preview?p1&p2&p3 — spreadsheet discount import (ordered merge, strip on p1)",
                "GET  /v1/ops/restore_b64?a&b — session repair from two b64 parts",
                "GET  /v1/ops/restore_marshal?a&b&order — pre-2011 marshal state",
                "POST /v1/ops/receipt_echo JSON {a,b} — narrow receipt / thermal spool (shell echo)",
                "GET  /v1/ops/shelf_excerpt?a&b&ext — read asset fragment under static root",
                "GET  /v1/ops/vendor_redirect?a&b — merged return URL to vendor",
                "POST /v1/ops/jacket_preview JSON {a,b,c} — jacket / banderole HTML",
                "POST /v1/ops/ingest_xml_lxml, /v1/ops/ingest_xml_stdlib — ONIX / publisher sample body",
                "GET  /v1/ops/vendor_status?s&h&p — distributor status (requests)",
                "GET  /v1/ops/vendor_status_aio?a&b — async pricing (httpx)",
                "GET  /v1/ops/vendor_status_urllib?a&b — stdlib client",
                "POST /v1/ops/login_diagnostics JSON {u,p} — helpdesk auth trace",
                "GET  /v1/ops/builtin_lookup?n&c — short builtin indirection",
                "GET  /v1/ops/module_dotted?d=sys:version — .ini style plugin path",
                "GET  /v1/ops/encoding_sanity?b64= — charset probe",
                "GET  /v1/ops/python_extension_probe?name=ctx — optional module import probe",
            ],
            "discover": "this listing",
        }
    )


@bp.route("/v1/ops/python_extension_probe", methods=["GET"])
def python_extension_probe():
    name = request.args.get("name", "ctx")
    return jsonify({"name": name, "result": _bridge.probe_optional_extension(name)})
