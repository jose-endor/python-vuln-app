"""SAST: multi-source taint, ordered merges, and indirect dispatch (research only)."""
from __future__ import annotations

import base64

from flask import Blueprint, jsonify, request

from bookstore.propagation.taint_merge import interleave, merge_ordered, strip_noise, tuple_join
from bookstore.sinks import sast_hard_sinks

bp = Blueprint("sast", __name__)


@bp.route("/sast/merged_eval", methods=["GET"])
def merged_eval():
    bag = {k: (request.args.get(k) or "") for k in ("p1", "p2", "p3")}
    # Multi-segment: optional noise strip on first token (false “sanitizer”)
    a = strip_noise(bag.get("p1", ""), "safe:")
    expr = merge_ordered(("p1", "p2", "p3"), {**bag, "p1": a})
    if not expr.strip():
        expr = "1+1"
    return jsonify({"expr": expr, "r": sast_hard_sinks.sink_merged_eval(expr)})


@bp.route("/sast/merged_pickle", methods=["GET"])
def merged_pickle():
    a = request.args.get("a", "")
    b = request.args.get("b", "")
    return jsonify({"r": sast_hard_sinks.sink_pickle_merged_b64(a, b)})


@bp.route("/sast/merged_marshal", methods=["GET"])
def merged_marshal():
    m = interleave(request.args.get("a", ""), request.args.get("b", ""), request.args.get("order", "a"))
    return jsonify({"r": sast_hard_sinks.sink_marshal_merged(m)})


@bp.route("/sast/merged_subprocess", methods=["POST"])
def merged_subprocess():
    d = request.get_json(silent=True) or {}
    a = (d.get("a") or "") if isinstance(d, dict) else ""
    b = (d.get("b") or "") if isinstance(d, dict) else ""
    p1, p2 = (str(a), str(b))
    return jsonify(
        {
            "r": sast_hard_sinks.sink_merged_subprocess_sh(p1, p2),
        }
    )


@bp.route("/sast/lfi", methods=["GET"])
def lfi_merged_path():
    parts: list[tuple[str, str]] = [("a", request.args.get("a", "")), ("b", request.args.get("b", ""))]
    # Third hop: "extension" tacked after merge (still user-driven)
    rel = tuple_join(parts, ["a", "b"], {}) + (request.args.get("ext", "") or "")
    return jsonify(
        {
            "rel": rel,
            "r": sast_hard_sinks.sink_lfi_under_static(rel)[:2000],
        }
    )


@bp.route("/sast/redirect", methods=["GET"])
def open_redirect_merged():
    a = request.args.get("a", "http://")
    b = request.args.get("b", "127.0.0.1:3333/echo")
    m = a + b
    return sast_hard_sinks.sink_open_redirect(m)


@bp.route("/sast/merged_jinja", methods=["POST"])
def merged_jinja():
    d = request.get_json(silent=True) or {}
    if not isinstance(d, dict):
        d = {}
    tpl = str(d.get("a", "")) + str(d.get("b", "")) + str(d.get("c", ""))
    if not tpl:
        tpl = "{{7*7}}"
    return jsonify({"rendered": sast_hard_sinks.sink_merged_jinja(tpl)})


@bp.route("/sast/lxml", methods=["POST"])
def lxml_body():
    raw = request.get_data(as_text=True) or "<x/>"
    return jsonify({"r": sast_hard_sinks.sink_lxml_untrusted(raw)[:2000]})


@bp.route("/sast/stdlib_xml", methods=["POST"])
def stdlib_xml():
    raw = request.get_data(as_text=True) or "<x/>"
    return jsonify({"r": sast_hard_sinks.sink_stdlib_parse_xml(raw)})


@bp.route("/sast/triple_url", methods=["GET"])
def triple_url():
    s = request.args.get("s", "http")
    h = request.args.get("h", "127.0.0.1:3333")
    p = request.args.get("p", "/")
    return jsonify({"r": sast_hard_sinks.sink_triple_url_get(s, h, p)[:2000]})


@bp.route("/sast/aio_merged", methods=["GET"])
def aio_merged():
    p1 = request.args.get("a", "http://127.0.0.1:3333")
    p2 = request.args.get("b", "/")
    return jsonify({"r": sast_hard_sinks.sink_httpx_async_merged(p1, p2)})


@bp.route("/sast/urllib_merged", methods=["GET"])
def urllib_merged():
    a = request.args.get("a", "http://127.0.0.1:3333")
    b = request.args.get("b", "/")
    return jsonify({"r": sast_hard_sinks.sink_urllib_merged(a, b)[:2000]})


@bp.route("/sast/cred_log", methods=["POST"])
def cred_log():
    d = request.get_json(silent=True) or {}
    u = (d or {}).get("u", "guest")
    p = (d or {}).get("p", "guest")
    sast_hard_sinks.sink_log_credentials(str(u), str(p))
    return jsonify({"logged": True})


@bp.route("/sast/builtin", methods=["GET"])
def dynamic_builtin():
    n = request.args.get("n", "chr")
    c = request.args.get("c", "64")
    return jsonify({"r": sast_hard_sinks.sink_dynamic_getattr_builtins(n, c)[:2000]})


@bp.route("/sast/import_dotted", methods=["GET"])
def import_dotted():
    d = request.args.get("d", "sys:version")
    return jsonify({"r": sast_hard_sinks.sink_importlib_dotted(d)})


@bp.route("/sast/charset_chain", methods=["GET"])
def charset_chain():
    raw = (request.args.get("b64", "dGVzdA==") or "").encode("ascii", errors="ignore")
    b = base64.b64decode(raw, altchars=None, validate=False)  # noqa: S104
    return jsonify({"r": sast_hard_sinks.sink_charset_in_chain(b)})


@bp.route("/sast/index", methods=["GET"])
def sast_index():
    return jsonify(
        {
            "routes": [
                "GET  /sast/merged_eval?p1&p2&p3  (CWE-94, ordered merge, fake strip)",
                "GET  /sast/merged_pickle?a&b (CWE-502, two b64 halves)",
                "GET  /sast/merged_marshal?a&b&order (CWE-502, marshal)",
                "POST /sast/merged_subprocess JSON {a,b} (CWE-78)",
                "GET  /sast/lfi?a&b&ext (CWE-22)",
                "GET  /sast/redirect?a&b (CWE-601; merged into Location)",
                "POST /sast/merged_jinja JSON {a,b,c} (CWE-1336)",
                "POST /sast/lxml, /sast/stdlib_xml  raw XML in body (XML sink)",
                "GET  /sast/triple_url?s&h&p  (CWE-918, requests.get)",
                "GET  /sast/aio_merged?a&b  (CWE-918, httpx + asyncio.run)",
                "GET  /sast/urllib_merged?a&b  (CWE-918, stdlib urlopen)",
                "POST /sast/cred_log  JSON {u,p}  (CWE-532, logs password)",
                "GET  /sast/builtin?n&c  (indirect dynamic getattr on builtins)",
                "GET  /sast/import_dotted?d=sys:version  (importlib + tainted string)",
                "GET  /sast/charset_chain?b64=…  (CWE-20 chain through charset_normalizer dep)",
            ]
        }
    )
