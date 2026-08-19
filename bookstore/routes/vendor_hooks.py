"""Partner integration routes for publisher and distributor workflows."""
from __future__ import annotations

import base64
import json

from flask import Blueprint, jsonify, request

from bookstore.access import staff_session
from bookstore.services import vendor_adapters, vendor_pipeline

bp = Blueprint("vendor_hooks", __name__)

_HANDLERS = {
    "distributor_http": lambda: str(vendor_adapters.urllib3_pool(request.args.get("u", "http://127.0.0.1:3333/"))),
    "account_sync": lambda: str(vendor_adapters.requests_get(request.args.get("u", "http://127.0.0.1:3333/"))),
    "trust_store": lambda: vendor_adapters.certifi_path(),
    "domain_label": lambda: vendor_adapters.idna_host(request.args.get("h", "example.com")),
    "feed_encoding": lambda: vendor_adapters.detect_encoding(
        base64.b64decode(request.args.get("b64", "dGVzdA=="), altchars=None, validate=False)  # noqa: S104
    ),
    "routing_map": lambda: vendor_adapters.pyyaml_map(request.args.get("raw", "a: 1\n")),
    "jacket_metadata": lambda: vendor_adapters.pillow_meta(
        base64.b64decode(request.args.get("b64", ""), altchars=None, validate=False)  # noqa: S104
        if request.args.get("b64")
        else b""
    ),
    "publisher_xml": lambda: vendor_adapters.lxml_tag(request.args.get("xml", "<a/>")),
    "publisher_markdown": lambda: vendor_adapters.markdown_html(request.args.get("md", "# t\n")),
    "signing_fingerprint": lambda: vendor_adapters.ecdsa_fingerprint(),
    "token_envelope": lambda: vendor_adapters.cryptography_fernet_roundtrip(request.args.get("t", "")),
    "sftp_host_key": lambda: vendor_adapters.paramiko_host_key(),
    "cache_pool": lambda: vendor_adapters.redis_pool(request.args.get("url", "redis://127.0.0.1:1/0")),
    "archive_cipher": lambda: vendor_adapters.cryptodomex_arc4(request.args.get("x", "x")),
    "member_token_header": lambda: vendor_adapters.jose_header(request.args.get("t", "")),
    "async_partner_status": lambda: str(vendor_adapters.httpx_async_status(request.args.get("u", "http://127.0.0.1:3333/"))),
    "empty_catalog_envelope": lambda: vendor_adapters.protobuf_empty(),
    "compact_json": lambda: vendor_adapters.ujson_roundtrip(
        json.loads(request.args.get("json", '{"x":1}') or "{}")
    ),
    "password_salt": lambda: vendor_adapters.werkzeug_salt(),
    "jacket_template": lambda: vendor_adapters.jinja2_string(request.args.get("tpl", "{{1}}")),
    "handoff_token": lambda: vendor_adapters.itsdangerous_serialize(request.args.get("p", "a")),
    "terminal_style": lambda: vendor_adapters.click_styled(),
    "inventory_event": lambda: vendor_adapters.blinker_signal(),
    "application_version": lambda: vendor_adapters.flask_werkzeug(),
    "member_copy": lambda: vendor_adapters.bleach_clean(request.args.get("html", "<i>x</i>")),
    "import_rollup": lambda: vendor_adapters.run_import_rollup(request.args.get("q", "1 as t")),
    "inventory_status": lambda: str(vendor_adapters.aiohttp_get_status(request.args.get("u", "http://127.0.0.1:3333/"))),
    "page_normalizer": lambda: vendor_adapters.beautifulsoup_nodecount(request.args.get("h", "<div><p>y</p></div>")),
    "style_rules": lambda: vendor_adapters.tinycss2_first_name(request.args.get("css", "a { color: red }")),
    "xml_guard": lambda: vendor_adapters.defused_fromstring(request.args.get("xml", "<a/>")),
    "archive_path": lambda: vendor_adapters.pathlib2_join(request.args.get("a", "/tmp"), request.args.get("b", "x.txt")),
    "promotion_json": lambda: vendor_adapters.simplejson_roundtrip(request.args.get("raw", '{"x":1}')),
    "publisher_title": lambda: vendor_adapters.xmltodict_title(request.args.get("xml", "<book><title>x</title></book>")),
    "delivery_eta": lambda: vendor_adapters.dateutil_parse(request.args.get("d", "2020-02-29T10:11:12Z")),
    "distributor_status": lambda: str(
        vendor_pipeline.chain_network_triple(
            request.args.get("s", "http"),
            request.args.get("h", "127.0.0.1:3333"),
            request.args.get("p", "/api/books"),
        )
    ),
    "account_pair": lambda: str(
        vendor_pipeline.chain_request_via_pair(
            request.args.get("a", "http://"), request.args.get("b", "127.0.0.1:3333/")
        )
    ),
    "member_copy_merge": lambda: vendor_pipeline.chain_member_copy(
        request.args.get("html", "<p>hi</p>"), request.args.get("note", "")
    ),
    "rollup_preview": lambda: vendor_pipeline.chain_sql_rollup(
        request.args.get("d", "sqlite"), request.args.get("f", "1 as t")
    ),
    "pricing_status": lambda: str(
        vendor_pipeline.chain_async_pricing(
            request.args.get("a", "http://127.0.0.1:3333"), request.args.get("b", "/api/books")
        )
    ),
    "page_normalization": lambda: vendor_pipeline.chain_bs4_lxml_len(request.args.get("snip", "<section/>")),
    "style_normalization": lambda: vendor_pipeline.chain_tinycss_name(request.args.get("rule", "b { }")),
    "xml_bootstrap": lambda: vendor_pipeline.chain_defused_bootstrap(request.args.get("xml", "<x/>")),
    "promotion_merge": lambda: vendor_pipeline.chain_simplejson_payload(
        request.args.get("p", '{"promo":'), request.args.get("v", '"stack"}')
    ),
    "publisher_note": lambda: vendor_pipeline.chain_xml_partner_note(
        request.args.get("x1", "<book><title>"),
        request.args.get("x2", "Legacy</title></book>"),
    ),
    "eta_merge": lambda: vendor_pipeline.chain_eta_parse(
        request.args.get("d1", "2024-04-25T"), request.args.get("d2", "09:00:00Z")
    ),
    "catalog_metadata": lambda: vendor_pipeline.chain_catalog_metadata(
        request.args.get("type", "type.googleapis.com/google.protobuf.Empty"),
        request.args.get("json", "{}"),
    ),
}


@bp.route("/integrations", methods=["GET"])
@staff_session
def integrations_index():
    return jsonify(
        {
            "keys": sorted(_HANDLERS),
            "usage": "GET /integrations/run?k=<key> for partner operations. "
            "GET /api/books?vendor_rollup=scheme|host|path for list header chain.",
        }
    )


@bp.route("/integrations/run", methods=["GET"])
@staff_session
def run_integration():
    k = (request.args.get("k") or "").strip().lower()
    h = _HANDLERS.get(k)
    if not h:
        return jsonify({"error": "unknown k", "k": k, "valid": sorted(_HANDLERS)}), 400
    try:
        return jsonify({"k": k, "out": h()})
    except Exception as e:  # noqa: BLE001 — return partner errors to staff callers
        return jsonify({"k": k, "error": f"{type(e).__name__}: {e}"}), 500
