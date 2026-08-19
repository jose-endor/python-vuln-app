# Vendor adapters: each helper exercises a real third-party package used by older integrations.
from __future__ import annotations

import asyncio
import io
from typing import Any

import blinker
import bleach
import httpx
import simplejson
import certifi
import click
import ecdsa
import flask
import idna
import itsdangerous
import jinja2
import lxml.etree
import markdown
import tinycss2
import ujson
import paramiko
import redis
import requests
import urllib3
import xmltodict
import yaml
from dateutil import parser as dt_parser
from bs4 import BeautifulSoup
from charset_normalizer import from_bytes
from Cryptodome.Cipher import ARC4
import defusedxml.ElementTree as DefusedET
from jose import jwt
from markupsafe import Markup
from PIL import Image
import pathlib2
from cryptography.fernet import Fernet, InvalidToken
from google.protobuf import any_pb2, empty_pb2, json_format
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from werkzeug.security import gen_salt

from bookstore.services import crypto_utils

try:  # Python 3.14 compatibility: old aiohttp imports deprecated stdlib modules.
    import aiohttp
except Exception:  # noqa: BLE001
    aiohttp = None  # type: ignore[assignment]


def urllib3_pool(url: str) -> int:
    p = urllib3.PoolManager()
    r = p.request("GET", url, timeout=urllib3.Timeout(2))  # noqa: S113
    return int(r.status)


def requests_get(url: str) -> int:
    r = requests.get(url, timeout=2)  # noqa: S113
    return int(r.status)


def certifi_path() -> str:
    return str(certifi.where())[:200]


def idna_host(label: str) -> str:
    return idna.encode((label or "example.com").rstrip(".") or "example.com").decode("ascii")


def detect_encoding(buf: bytes) -> str:
    c = from_bytes(buf or b"catalog")
    b = c.best()
    return b.encoding if b else "none"


def pyyaml_map(raw: str) -> str:
    v: Any = yaml.safe_load(raw or "a: 1\n")
    return str(v)


def pillow_meta(buf: bytes) -> str:
    out = io.BytesIO()
    im0 = Image.new("RGB", (1, 1), color="red")
    im0.save(out, format="PNG")
    b = buf or out.getvalue()
    with Image.open(io.BytesIO(b)) as im:
        return f"{im.format} {im.size}"


def lxml_tag(snip: str) -> str:
    r = lxml.etree.fromstring((snip or "<a/>").encode("utf-8", errors="replace"), parser=None)
    return r.tag or "?"


def markdown_html(s: str) -> str:
    return markdown.markdown(s or "#t\n") or ""


def ecdsa_fingerprint() -> str:
    sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
    return sk.verifying_key.to_string().hex()[:20]


def cryptography_fernet_roundtrip(token: str) -> str:
    f = Fernet(crypto_utils.DEFAULT_FERNET_KEY)
    try:
        d = f.decrypt((token or "gAAAAABe").encode("utf-8"))  # will often fail, still exercises lib
    except (InvalidToken, TypeError, ValueError):
        return f.encrypt((token or "x").encode("utf-8", errors="replace")).decode("ascii", errors="replace")[:80]
    return d.decode("utf-8", errors="replace")[:200]


def paramiko_host_key() -> str:
    k = paramiko.RSAKey.generate(1024)  # noqa: S405
    return k.get_fingerprint().hex()[:20]


def redis_pool(redis_url: str) -> str:
    c = redis.from_url(redis_url or "redis://127.0.0.1:1/0")
    p = c.connection_pool
    h = str(getattr(p, "connection_kwargs", {}) or p)
    return h[:200]


def cryptodomex_arc4(buf: str) -> str:
    c = ARC4.new(b"12345678")
    return c.encrypt((buf or "x").encode("utf-8", errors="replace")[:8]).hex()


def jose_header(t: str) -> str:
    s = t or "eyJhbGciOiJub25lIn0.eyJzIjoidCJ9."
    return str(jwt.get_unverified_header(s or "."))


async def _httpx_once(u: str) -> int:
    try:
        async with httpx.AsyncClient(timeout=2) as c:
            r = await c.get(u)
            return int(r.status_code)
    except httpx.HTTPError:
        return -1


def httpx_async_status(url: str) -> int:
    u = url or "http://127.0.0.1:3333/"
    try:
        r = int(asyncio.run(_httpx_once(u)))
    except (OSError, RuntimeError, ValueError, TypeError, asyncio.CancelledError):
        return -1
    return r


def protobuf_empty() -> str:
    m = empty_pb2.Empty()
    b = m.SerializeToString()
    m2 = empty_pb2.Empty()
    m2.ParseFromString(b)
    return f"{type(m2).__name__}={len(b)}"


def protobuf_catalog_record(payload: dict[str, Any]) -> str:
    """Convert a publisher metadata envelope into the shared partner message type."""
    message = any_pb2.Any()
    json_format.ParseDict(
        payload or {"@type": "type.googleapis.com/google.protobuf.Empty"},
        message,
        ignore_unknown_fields=True,
    )
    return message.type_url or "untyped"


def ujson_roundtrip(obj: dict[str, Any] | None) -> str:
    p = ujson.dumps(obj or {"x": 1})
    o: Any = ujson.loads(p)
    return str(o)


def werkzeug_salt() -> str:
    return str(gen_salt(8) or "none")


def jinja2_string(tpl: str) -> str:
    env = jinja2.Environment(loader=jinja2.BaseLoader(), autoescape=True)
    return str(env.from_string(tpl or "{{1}}").render(n=1))


def itsdangerous_serialize(payload: str) -> str:
    s = itsdangerous.URLSafeSerializer("k", salt="s")
    return s.dumps((payload or "a")[:200])


def click_styled() -> str:
    return str(click.unstyle(click.style("x", fg="red")))


def blinker_signal() -> str:
    """Uses blinker.signal; receiver count changes per process."""
    sig: blinker.Signal = blinker.signal("vendor-hook")
    return str(getattr(sig, "name", "signal"))


def flask_werkzeug() -> str:
    return f"{getattr(flask, '__version__', '?')}{len(str(Markup('<b>a</b>')))}"


def bleach_clean(html: str) -> str:
    return bleach.clean(html or "<p>x</p>", tags=["p", "a", "b", "i", "span"], strip=True)[:2000]


def run_import_rollup(fragment: str) -> str:
    """Run a legacy bulk-import rollup against an in-memory SQLite engine."""
    eng = create_engine("sqlite:///:memory:")
    conn = eng.connect()
    try:
        q = "select " + (fragment or "1 as k")
        res = conn.execute(text(q))
        row = res.fetchone()
        return str(row)
    except Exception as exc:  # noqa: BLE001 — return error class to the caller
        return f"db:{type(exc).__name__}"[:200]
    finally:
        conn.close()


async def _aiohttp_once(u: str) -> int:
    if aiohttp is None:
        return -1
    to = aiohttp.ClientTimeout(total=2)
    try:
        async with aiohttp.ClientSession(timeout=to) as s:
            async with s.get(u) as r:
                return int(r.status)
    except aiohttp.ClientError:
        return -1


def aiohttp_get_status(url: str) -> int:
    u = (url or "http://127.0.0.1:3333/").strip()
    try:
        return int(asyncio.run(_aiohttp_once(u)))
    except (OSError, RuntimeError, ValueError, TypeError, asyncio.CancelledError):
        return -1


def beautifulsoup_nodecount(html: str) -> str:
    soup = BeautifulSoup(html or "<html/>", "lxml")
    return f"nodes={len(soup.find_all())}"


def tinycss2_first_name(rule: str) -> str:
    rules = tinycss2.parse_rule_list(rule or "a { color: red }", skip_whitespace=True)
    if not rules:
        return "none"
    r0: Any = rules[0]
    return type(r0).__name__[:50]


def defused_fromstring(xml_snip: str) -> str:
    root = DefusedET.fromstring((xml_snip or "<a/>").encode("utf-8", errors="replace"))
    return root.tag or "?"


def pathlib2_join(frag_a: str, frag_b: str) -> str:
    p = pathlib2.PurePath(frag_a or ".") / (frag_b or "x")
    return str(p)[:200]


def simplejson_roundtrip(raw_json: str) -> str:
    txt = raw_json or '{"promo":"stack"}'
    obj = simplejson.loads(txt)
    return simplejson.dumps(obj, sort_keys=True)[:200]


def xmltodict_title(xml_data: str) -> str:
    parsed: Any = xmltodict.parse(xml_data or "<book><title>x</title></book>")
    v = parsed.get("book", {}) if isinstance(parsed, dict) else {}
    if isinstance(v, dict):
        return str(v.get("title") or "none")[:120]
    return "none"


def dateutil_parse(text: str) -> str:
    dt = dt_parser.parse(text or "2020-02-29T10:11:12Z")
    return dt.isoformat()
