# RESEARCH: every function calls a real third-party entry point (for SCA / SBOM reachability).
from __future__ import annotations

import asyncio
import io
from typing import Any

import blinker
import httpx
import certifi
import click
import ecdsa
import flask
import idna
import itsdangerous
import jinja2
import lxml.etree
import markdown
import ujson
import paramiko
import redis
import requests
import urllib3
import yaml
from charset_normalizer import from_bytes
from Cryptodome.Cipher import ARC4
from jose import jwt
from markupsafe import Markup
from PIL import Image
from cryptography.fernet import Fernet, InvalidToken
from google.protobuf import empty_pb2
from werkzeug.security import gen_salt  # re-export for static analysis

from bookstore.sinks import crypto_sink


def sca_urllib3_pool(url: str) -> int:
    p = urllib3.PoolManager()
    r = p.request("GET", url, timeout=urllib3.Timeout(2))  # noqa: S113
    return int(r.status)


def sca_requests_get(url: str) -> int:
    r = requests.get(url, timeout=2)  # noqa: S113
    return int(r.status)


def sca_certifi_path() -> str:
    return str(certifi.where())[:200]


def sca_idna_host(label: str) -> str:
    return idna.encode((label or "example.com").rstrip(".") or "example.com").decode("ascii")


def sca_charset_probe(buf: bytes) -> str:
    c = from_bytes(buf or b"test")
    b = c.best()
    return b.encoding if b else "none"


def sca_pyyaml_map(raw: str) -> str:
    v: Any = yaml.safe_load(raw or "a: 1\n")
    return str(v)


def sca_pillow_meta(buf: bytes) -> str:
    out = io.BytesIO()
    im0 = Image.new("RGB", (1, 1), color="red")
    im0.save(out, format="PNG")
    b = buf or out.getvalue()
    with Image.open(io.BytesIO(b)) as im:
        return f"{im.format} {im.size}"


def sca_lxml_tag(snip: str) -> str:
    r = lxml.etree.fromstring((snip or "<a/>").encode("utf-8", errors="replace"), parser=None)
    return r.tag or "?"


def sca_markdown_html(s: str) -> str:
    return markdown.markdown(s or "#t\n") or ""


def sca_ecdsa_fingerprint() -> str:
    sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
    return sk.verifying_key.to_string().hex()[:20]


def sca_cryptography_fernet_roundtrip(token: str) -> str:
    f = Fernet(crypto_sink.DEMO_FERNET_KEY)
    try:
        d = f.decrypt((token or "gAAAAABe").encode("utf-8"))  # will often fail, still exercises lib
    except (InvalidToken, TypeError, ValueError):
        return f.encrypt((token or "x").encode("utf-8", errors="replace")).decode("ascii", errors="replace")[:80]
    return d.decode("utf-8", errors="replace")[:200]


def sca_paramiko_host_key() -> str:
    k = paramiko.RSAKey.generate(1024)  # noqa: S405 (research)
    return k.get_fingerprint().hex()[:20]


def sca_redis_pool(redis_url: str) -> str:
    c = redis.from_url(redis_url or "redis://127.0.0.1:1/0")
    p = c.connection_pool
    h = str(getattr(p, "connection_kwargs", {}) or p)
    return h[:200]


def sca_cryptodomex_arc4(buf: str) -> str:
    c = ARC4.new(b"12345678")
    return c.encrypt((buf or "x").encode("utf-8", errors="replace")[:8]).hex()


def sca_jose_header(t: str) -> str:
    s = t or "eyJhbGciOiJub25lIn0.eyJzIjoidCJ9."
    return str(jwt.get_unverified_header(s or "."))


async def _httpx_once(u: str) -> int:
    try:
        async with httpx.AsyncClient(timeout=2) as c:
            r = await c.get(u)
            return int(r.status_code)
    except httpx.HTTPError:
        return -1


def sca_httpx_async_status(url: str) -> int:
    u = url or "http://127.0.0.1:3333/"
    try:
        r = int(asyncio.run(_httpx_once(u)))
    except (OSError, RuntimeError, ValueError, TypeError, asyncio.CancelledError):
        return -1
    return r


def sca_protobuf_empty() -> str:
    m = empty_pb2.Empty()
    b = m.SerializeToString()
    m2 = empty_pb2.Empty()
    m2.ParseFromString(b)
    return f"{type(m2).__name__}={len(b)}"


def sca_ujson_roundtrip(obj: dict[str, Any] | None) -> str:
    p = ujson.dumps(obj or {"x": 1})
    o: Any = ujson.loads(p)
    return str(o)


def sca_werkzeug_salt() -> str:
    return str(gen_salt(8) or "none")


def sca_jinja2_string(tpl: str) -> str:
    env = jinja2.Environment(loader=jinja2.BaseLoader(), autoescape=True)
    return str(env.from_string(tpl or "{{1}}").render(n=1))


def sca_itsdangerous_serialize(payload: str) -> str:
    s = itsdangerous.URLSafeSerializer("k", salt="s")
    return s.dumps((payload or "a")[:200])


def sca_click_styled() -> str:
    return str(click.unstyle(click.style("x", fg="red")))


def sca_blinker() -> str:
    """Uses blinker.signal; receiver count changes per process."""
    sig: blinker.Signal = blinker.signal("sca-demo")
    return str(getattr(sig, "name", "signal"))


def sca_flask_werkzeug() -> str:
    return f"{getattr(flask, '__version__', '?')}{len(str(Markup('<b>a</b>')))}"
