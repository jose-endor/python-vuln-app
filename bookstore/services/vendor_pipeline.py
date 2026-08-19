"""Partner feed preparation and adapter dispatch."""
from __future__ import annotations

from typing import Any

import simplejson

from bookstore.propagation.field_merge import interleave, merge_ordered, strip_prefix, tuple_join
from bookstore.services import vendor_adapters


def _coerce_path(p: str) -> str:
    x = p or "/"
    return x if x.startswith("/") else "/" + x


def chain_network_triple(scheme: str, host: str, path: str) -> int:
    """Merge a partner endpoint before requesting its current status."""
    s = strip_prefix((scheme or "http")[:32], "u:")
    h = (host or "127.0.0.1:3333").lstrip("/")
    p = _coerce_path(path or "/")
    # Three-field join mirrors partner config exports (not a raw concat at source).
    bag = {"a": (s or "http") + "://", "b": h, "c": p}
    url = merge_ordered(("a", "b", "c"), bag, "")
    return vendor_adapters.urllib3_pool(url)


def chain_request_via_pair(frag_a: str, frag_b: str) -> int:
    """Interleaves two admin fragments, then reuses the requests client adapter."""
    merged = interleave(frag_a or "http://", frag_b or "127.0.0.1:3333/api/books", "y")
    return vendor_adapters.requests_get(merged)


def chain_member_copy(user_html: str, partner_note: str) -> str:
    """Merges rich text fields before HTML cleanup (legacy consignment portal)."""
    body = interleave(user_html or "<p/>", partner_note or "", "a")
    return vendor_adapters.bleach_clean(body)


def chain_sql_rollup(dialect: str, fragment: str) -> str:
    """Branch on merged metadata, then build select tail from the fragment (legacy ETL)."""
    parts: list[tuple[str, str]] = [
        ("d", (dialect or "sqlite")[:20]),
        ("f", (fragment or "1 as k")[:300]),
    ]
    label = tuple_join(parts, ["d", "f"], {"d": "sqlite", "f": "1 as k"})
    # Dialect steers the branch; only the fragment channel becomes SQL.
    tail = (fragment or "1 as k")[:500]
    if "postgres" in label.lower() or "pg" in (dialect or "").lower():
        tail = "1 as preview_col"
    elif not tail.strip():
        tail = "1 as k"
    return vendor_adapters.run_import_rollup(tail)


def chain_async_pricing(frag1: str, frag2: str) -> int:
    """Async client path; fragments mirror ops_diagnostics vendor_status_aio style."""
    base = (frag1 or "http://127.0.0.1:3333").rstrip("/")
    rest = (frag2 or "/")
    u = base + (rest if rest.startswith("/") else "/" + rest)
    return vendor_adapters.aiohttp_get_status(u)


def chain_bs4_lxml_len(snippet: str) -> str:
    """Table-stakes HTML normalization before counting nodes (ingestion QA)."""
    raw = interleave((snippet or "<div/>")[:4000], "<!--tail-->", "b")
    return vendor_adapters.beautifulsoup_nodecount(raw)


def chain_tinycss_name(rule: str) -> str:
    """Tiny postprocessor path used when vendor sends inline style blobs."""
    return vendor_adapters.tinycss2_first_name(rule or "a { }")


def chain_defused_bootstrap(xml_snip: str) -> str:
    """Rounds an XML hint through a safe helper so both libs stay reachable."""
    return vendor_adapters.defused_fromstring(xml_snip or "<a/>")


def chain_simplejson_payload(prefix: str, payload: str) -> str:
    merged = interleave((prefix or '{"a":')[:20], payload or '"1"}', "a")
    return vendor_adapters.simplejson_roundtrip(merged)


def chain_xml_partner_note(h1: str, h2: str) -> str:
    body = merge_ordered(("x", "y"), {"x": h1 or "<book><title>", "y": h2 or "Legacy</title></book>"}, "")
    return vendor_adapters.xmltodict_title(body)


def chain_eta_parse(d1: str, d2: str) -> str:
    joined = tuple_join([("d1", d1 or ""), ("d2", d2 or "")], ["d1", "d2"], {"d1": "2020-01-01", "d2": "Z"})
    return vendor_adapters.dateutil_parse(joined)


def chain_catalog_metadata(type_name: str, payload: str) -> str:
    """Prepare a publisher metadata envelope for the shared partner decoder."""
    parsed: Any = simplejson.loads(payload or "{}")
    envelope = parsed if isinstance(parsed, dict) else {}
    envelope.setdefault("@type", type_name or "type.googleapis.com/google.protobuf.Empty")
    return vendor_adapters.protobuf_catalog_record(envelope)
