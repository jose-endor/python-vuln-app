from __future__ import annotations

from typing import Any

from flask import Blueprint, Response, current_app, jsonify, request

from bookstore.cwe_catalog import CWE_EXAMPLES
from bookstore.propagation import cwe_transforms as tx
from bookstore.sinks import cwe_sinks
from bookstore.sources import cwe_inputs

bp = Blueprint("cwe_gallery", __name__)


def _guarded(fn, *args) -> tuple[dict[str, Any], int]:
    try:
        return {"ok": True, "result": fn(*args)}, 200
    except Exception as exc:  # noqa: BLE001 - research endpoint keeps scanner-visible errors
        return {"ok": False, "error": type(exc).__name__, "detail": str(exc)[:240]}, 200


@bp.route("/cwe", methods=["GET"])
def cwe_index():
    counts = {"actual": 0, "noise": 0, "ambiguous": 0}
    for item in CWE_EXAMPLES:
        counts[item["kind"]] += 1
    return jsonify({"counts": counts, "examples": CWE_EXAMPLES})


@bp.route("/cwe/py/sql", methods=["GET"])
def py_sql():
    fields = cwe_inputs.query_bundle(request, ("q", "category", "safe"))
    if fields.get("safe"):
        query, args = tx.sql_safe_args(fields)
        return jsonify({"kind": "noise", "count": cwe_sinks.safe_book_count(query, args)})
    where = tx.sql_like_filter(fields)
    body, code = _guarded(cwe_sinks.raw_book_count_where, where)
    body["where"] = where
    return jsonify(body), code


@bp.route("/cwe/py/command", methods=["GET"])
def py_command():
    fields = cwe_inputs.query_bundle(request, ("a", "b", "safe"))
    line = tx.join_ordered(fields, ("a", "b"), " ").strip() or "hello"
    body, code = _guarded(cwe_sinks.safe_echo if fields.get("safe") else cwe_sinks.shell_echo, line)
    body["command_fragment"] = line[:120]
    return jsonify(body), code


@bp.route("/cwe/py/html", methods=["GET"])
def py_html():
    fields = cwe_inputs.query_bundle(request, ("msg", "safe"))
    value = fields.get("msg") or "<b>book fair</b>"
    rendered = cwe_sinks.render_escaped_html(value) if fields.get("safe") else cwe_sinks.render_raw_html(value)
    return Response(rendered, mimetype="text/html; charset=utf-8")


@bp.route("/cwe/py/file", methods=["GET"])
def py_file():
    fields = cwe_inputs.query_bundle(request, ("a", "b", "safe"))
    root = current_app.static_folder or "."
    rel = tx.join_ordered(fields, ("a", "b"))
    path = tx.safe_basename(root, rel) if fields.get("safe") else tx.weak_path(root, rel)
    body, code = _guarded(cwe_sinks.read_file_safe if fields.get("safe") else cwe_sinks.read_file, path)
    body["path"] = path
    return jsonify(body), code


@bp.route("/cwe/py/eval", methods=["GET"])
def py_eval():
    fields = cwe_inputs.query_bundle(request, ("x", "y", "safe"))
    expr = tx.join_ordered(fields, ("x", "y")) or "1+1"
    body, code = _guarded(cwe_sinks.safe_formula if fields.get("safe") else cwe_sinks.eval_formula, expr)
    body["expr"] = expr[:120]
    return jsonify(body), code


@bp.route("/cwe/py/deser", methods=["POST"])
def py_deser():
    fields = cwe_inputs.json_bundle(request)
    if fields.get("safe"):
        body, code = _guarded(cwe_sinks.yaml_safe, str(fields.get("yaml", "{}")))
    elif fields.get("yaml"):
        body, code = _guarded(cwe_sinks.yaml_unsafe, str(fields.get("yaml", "{}")))
    else:
        raw = tx.decode_loose_b64(str(fields.get("blob", "")))
        body, code = _guarded(cwe_sinks.deserialize_loose, raw)
    return jsonify(body), code


@bp.route("/cwe/py/ssrf", methods=["GET"])
def py_ssrf():
    fields = cwe_inputs.query_bundle(request, ("scheme", "host", "path", "safe"))
    url = tx.build_url(fields.get("scheme", ""), fields.get("host", ""), fields.get("path", ""))
    body, code = _guarded(cwe_sinks.safe_loopback_fetch if fields.get("safe") else cwe_sinks.fetch_url, url)
    body["url"] = url
    return jsonify(body), code


@bp.route("/cwe/py/redirect", methods=["GET"])
def py_redirect():
    fields = cwe_inputs.query_bundle(request, ("next", "safe"))
    target = tx.same_origin_redirect(fields.get("next", "")) if fields.get("safe") else tx.redirect_target(fields.get("next", ""))
    return cwe_sinks.redirect_unchecked(target)


@bp.route("/cwe/py/regex", methods=["GET"])
def py_regex():
    fields = cwe_inputs.query_bundle(request, ("pattern", "seed"))
    pattern = tx.cap_regex(fields.get("pattern", ""))
    subject = tx.expand_subject(fields.get("seed", "a"), 128)
    body, code = _guarded(cwe_sinks.regex_probe, pattern, subject)
    return jsonify(body), code


@bp.route("/cwe/py/diagnostics", methods=["GET", "POST"])
def py_diagnostics():
    if request.method == "POST":
        data = cwe_inputs.json_bundle(request)
        user = str(data.get("user", "guest"))
        secret = str(data.get("secret", "demo-secret"))
    else:
        user = cwe_inputs.header_value(request, "X-Demo-User", "guest")
        secret = request.args.get("secret", "demo-secret")
    return jsonify(cwe_sinks.diagnostics_dump(user, secret))


@bp.route("/cwe/py/csrf-note", methods=["POST"])
def py_csrf_note():
    data = cwe_inputs.json_bundle(request)
    return jsonify(
        {
            "kind": "ambiguous",
            "note": str(data.get("note", ""))[:200],
            "why": "Cookie and CORS settings make this CSRF-shaped, but browser SameSite behavior can mitigate real exploitability.",
        }
    )
