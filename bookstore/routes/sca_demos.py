"""SCA: one route dispatches to many real dependency call sites (SBOM / reachability)."""
from __future__ import annotations

import base64
import json

from flask import Blueprint, jsonify, request

from bookstore.sinks import sca_chain, sca_stubs

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
    "bleach": lambda: sca_stubs.sca_bleach_clean(request.args.get("html", "<i>x</i>")),
    "sqlalchemy": lambda: sca_stubs.sca_sqlalchemy_probe(request.args.get("q", "1 as t")),
    "aiohttp": lambda: str(sca_stubs.sca_aiohttp_get_status(request.args.get("u", "http://127.0.0.1:3333/"))),
    "bs4": lambda: sca_stubs.sca_beautifulsoup_nodecount(request.args.get("h", "<div><p>y</p></div>")),
    "tinycss2": lambda: sca_stubs.sca_tinycss2_first_name(request.args.get("css", "a { color: red }")),
    "defusedxml": lambda: sca_stubs.sca_defused_fromstring(request.args.get("xml", "<a/>")),
    "pathlib2": lambda: sca_stubs.sca_pathlib2_join(request.args.get("a", "/tmp"), request.args.get("b", "x.txt")),
    "simplejson": lambda: sca_stubs.sca_simplejson_roundtrip(request.args.get("raw", '{"x":1}')),
    "xmltodict": lambda: sca_stubs.sca_xmltodict_title(request.args.get("xml", "<book><title>x</title></book>")),
    "dateutil": lambda: sca_stubs.sca_dateutil_parse(request.args.get("d", "2020-02-29T10:11:12Z")),
    "chain_net": lambda: str(
        sca_chain.chain_network_triple(
            request.args.get("s", "http"),
            request.args.get("h", "127.0.0.1:3333"),
            request.args.get("p", "/api/books"),
        )
    ),
    "chain_pair": lambda: str(
        sca_chain.chain_request_via_pair(request.args.get("a", "http://"), request.args.get("b", "127.0.0.1:3333/"))
    ),
    "chain_sanitize": lambda: sca_chain.chain_sanitize_cascade(
        request.args.get("html", "<p>hi</p>"), request.args.get("note", "")
    ),
    "chain_sql": lambda: sca_chain.chain_sql_rollup(request.args.get("d", "sqlite"), request.args.get("f", "1 as t")),
    "chain_async": lambda: str(
        sca_chain.chain_async_pricing(
            request.args.get("a", "http://127.0.0.1:3333"), request.args.get("b", "/api/books")
        )
    ),
    "chain_bs4": lambda: sca_chain.chain_bs4_lxml_len(request.args.get("snip", "<section/>")),
    "chain_tinycss": lambda: sca_chain.chain_tinycss_name(request.args.get("rule", "b { }")),
    "chain_defused": lambda: sca_chain.chain_defused_bootstrap(request.args.get("xml", "<x/>")),
    "chain_simplejson": lambda: sca_chain.chain_simplejson_payload(request.args.get("p", '{"promo":'), request.args.get("v", '"stack"}')),
    "chain_xml": lambda: sca_chain.chain_xml_partner_note(
        request.args.get("x1", "<book><title>"),
        request.args.get("x2", "Legacy</title></book>"),
    ),
    "chain_dateutil": lambda: sca_chain.chain_eta_parse(request.args.get("d1", "2024-04-25T"), request.args.get("d2", "09:00:00Z")),
}


@bp.route("/sca", methods=["GET"])
def sca_index():
    return jsonify(
        {
            "keys": sorted(_HANDLERS),
            "usage": "GET /sca/run?k=<key> — chain_* and adapters; see sca_demos for query params. GET /api/books?vendor_rollup=scheme|host|path for list header chain.",
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
