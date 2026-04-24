"""SCA: one route dispatches to many real dependency call sites (SBOM / reachability)."""
from __future__ import annotations

import base64
import json

from flask import Blueprint, jsonify, request

from bookstore.sinks import sca_stubs

bp = Blueprint("sca", __name__)

_HANDLERS = {
    "urllib3": lambda: str(sca_stubs.sca_urllib3_pool(request.args.get("u", "http://127.0.0.1:3333/"))),
    "requests": lambda: str(sca_stubs.sca_requests_get(request.args.get("u", "http://127.0.0.1:3333/"))),
    "certifi": lambda: sca_stubs.sca_certifi_path(),
    "idna": lambda: sca_stubs.sca_idna_host(request.args.get("h", "example.com")),
    "charset_normalizer": lambda: sca_stubs.sca_charset_probe(
        base64.b64decode(request.args.get("b64", "dGVzdA=="), altchars=None, validate=False)  # noqa: S104
    ),
    "pyyaml": lambda: sca_stubs.sca_pyyaml_map(request.args.get("raw", "a: 1\n")),
    "pillow": lambda: sca_stubs.sca_pillow_meta(
        base64.b64decode(request.args.get("b64", ""), altchars=None, validate=False)  # noqa: S104
        if request.args.get("b64")
        else b""
    ),
    "lxml": lambda: sca_stubs.sca_lxml_tag(request.args.get("xml", "<a/>")),
    "markdown": lambda: sca_stubs.sca_markdown_html(request.args.get("md", "# t\n")),
    "ecdsa": lambda: sca_stubs.sca_ecdsa_fingerprint(),
    "cryptography_fernet": lambda: sca_stubs.sca_cryptography_fernet_roundtrip(request.args.get("t", "")),
    "paramiko": lambda: sca_stubs.sca_paramiko_host_key(),
    "redis": lambda: sca_stubs.sca_redis_pool(request.args.get("url", "redis://127.0.0.1:1/0")),
    "pycryptodomex": lambda: sca_stubs.sca_cryptodomex_arc4(request.args.get("x", "x")),
    "jose": lambda: sca_stubs.sca_jose_header(request.args.get("t", "")),
    "httpx": lambda: str(sca_stubs.sca_httpx_async_status(request.args.get("u", "http://127.0.0.1:3333/"))),
    "protobuf": lambda: sca_stubs.sca_protobuf_empty(),
    "ujson": lambda: sca_stubs.sca_ujson_roundtrip(
        json.loads(request.args.get("json", '{"x":1}') or "{}")
    ),
    "werkzeug": lambda: sca_stubs.sca_werkzeug_salt(),
    "jinja2": lambda: sca_stubs.sca_jinja2_string(request.args.get("tpl", "{{1}}")),
    "itsdangerous": lambda: sca_stubs.sca_itsdangerous_serialize(request.args.get("p", "a")),
    "click": lambda: sca_stubs.sca_click_styled(),
    "blinker": lambda: sca_stubs.sca_blinker(),
    "flask_markupsafe": lambda: sca_stubs.sca_flask_werkzeug(),
}


@bp.route("/sca", methods=["GET"])
def sca_index():
    return jsonify(
        {
            "keys": sorted(_HANDLERS),
            "usage": "GET /sca/run?k=<key> — optional u, t, b64, xml, … (see sca_demos source).",
        }
    )


@bp.route("/sca/run", methods=["GET"])
def sca_run():
    k = (request.args.get("k") or "").strip().lower()
    h = _HANDLERS.get(k)
    if not h:
        return jsonify({"error": "unknown k", "k": k, "valid": sorted(_HANDLERS)}), 400
    try:
        return jsonify({"k": k, "out": h()})
    except Exception as e:  # noqa: BLE001 — research route surfaces errors
        return jsonify({"k": k, "error": f"{type(e).__name__}: {e}"}), 500
