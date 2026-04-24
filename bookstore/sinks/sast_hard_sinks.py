# RESEARCH: intentional sinks for SAST / taint-bench tooling.
from __future__ import annotations

import base64
import importlib
import io
import logging
import os
import pickle
import subprocess
import urllib.error
import urllib.request
import xml.etree.ElementTree as std_et

import httpx
import jinja2
import requests
from charset_normalizer import from_bytes
from flask import current_app, redirect, Response
from lxml import etree

# Hard sinks use library calls already in the graph; multi-step taint is in routes.
_LOG = logging.getLogger("sast_research")
_LOG.setLevel(logging.INFO)
if not _LOG.handlers:
    h = logging.StreamHandler()
    _LOG.addHandler(h)


def sink_merged_eval(expr: str) -> str:
    # CWE-95 / CWE-94: dynamic evaluation (research; localhost use only)
    g = {"__builtins__": __builtins__}
    return str(eval(expr, g, {}))  # noqa: S307


def sink_merged_pickle(blob: bytes) -> str:
    # CWE-502: object deserialization
    data = pickle.loads(blob)  # noqa: S301
    return repr(data)


def sink_merged_subprocess_sh(part_a: str, part_b: str) -> str:
    # CWE-78: shell with merged operands (multi-hop from sources)
    merged = f"{(part_a or '')} {(part_b or '')}".strip()
    return subprocess.check_output("echo " + merged, shell=True, text=True, stderr=subprocess.STDOUT)  # noqa: S602


def sink_lfi_under_static(sub_path: str) -> str:
    # CWE-22: path from merged segments before open()
    base = current_app.static_folder or "."
    path = os.path.join(base, (sub_path or ""))
    with open(path, "r", encoding="utf-8", errors="replace") as fh:  # noqa: SIM115
        return fh.read(8000)


def sink_open_redirect(merged: str) -> Response:
    # CWE-601: unvalidated target passed to redirect
    return redirect(merged, 302)  # noqa: S104


def sink_merged_jinja(template_body: str) -> str:
    # CWE-1336: SSTI
    env = jinja2.Environment(loader=jinja2.BaseLoader(), autoescape=False)
    return env.from_string(template_body).render({})


def sink_lxml_untrusted(user_xml: str) -> str:
    t = etree.parse(io.BytesIO((user_xml or "<x/>").encode("utf-8", errors="replace")))
    r = t.getroot()
    if r is not None and r.text:
        return (r.text or "")[:2000]
    if r is not None:
        return f"<{r.tag} children={len(r)}/>"[:2000]
    return "empty"


def sink_stdlib_parse_xml(user_xml: str) -> str:
    t = std_et.parse(io.StringIO(user_xml or "<x/>"), parser=None)
    root = t.getroot()
    if root is None:
        return "empty"
    return f"{root.tag} {len(list(root))} { (root.text or '')[:200]}"


def sink_triple_url_get(scheme: str, host: str, path: str) -> str:
    s = (scheme or "http").split("://")[0] or "http"
    h = (host or "127.0.0.1:3333").lstrip("/")
    p = path or "/"
    if not p.startswith("/"):
        p = "/" + p
    u = f"{s}://{h}{p}"
    r = requests.get(u, timeout=3)
    return f"{r.status_code} {r.text[:1500]}"


def sink_httpx_async_merged(
    p1: str,
    p2: str,
) -> str:
    # CWE-918: async httpx + asyncio.run; second graph vs requests/urllib3
    url = f"{(p1 or '')}{(p2 or '')}"

    async def _run() -> int:
        try:
            async with httpx.AsyncClient(timeout=2) as c:
                r = await c.get(url)
                return r.status_code
        except httpx.HTTPError:
            return -1

    import asyncio

    try:
        code = asyncio.run(_run())
    except (OSError, ValueError, RuntimeError, TypeError):
        return "async-err"
    return str(code)


def sink_log_credentials(user: str, password: str) -> None:
    # CWE-532: sensitive data in log message
    _LOG.info("login-attempt user=%r password=%r", user, password)


def sink_dynamic_getattr_builtins(name: str, code: str) -> str:
    # Indirect dynamic callsite on builtins
    b = __builtins__
    fn = getattr(b, (name or "").split(".")[-1], None)
    if not callable(fn):
        return f"not-callable:{name!r}"
    return str(fn(code))


def sink_importlib_dotted(dotted: str) -> str:
    # Tainted “module:attr” split across request fields
    mname, _, attr = (dotted or "sys:version").partition(":")
    m = importlib.import_module(mname or "sys")
    if not attr:
        return repr(m)
    return repr(getattr(m, attr, None))


def sink_charset_in_chain(buf: bytes) -> str:
    c = from_bytes(buf or b"")
    if not c:
        return "empty"
    b = c.best()
    return b.encoding if b and b.encoding else "uk"


def sink_pickle_merged_b64(
    a: str,
    b: str,
) -> str:
    # Two-fragment b64 reassembly before unsafe loads
    raw = base64.b64decode((a or "") + (b or ""), altchars=None, validate=False)  # noqa: S104
    return sink_merged_pickle(raw)


def sink_urllib_merged(
    a: str,
    b: str,
) -> str:
    u = (a or "") + (b or "")
    try:
        with urllib.request.urlopen(u, timeout=3) as r:
            body = r.read(4000)
            return body.decode("utf-8", "replace")
    except urllib.error.URLError as e:
        return f"urlobj:{e!r}"


def sink_marshal_merged(merged_b64: str) -> str:
    # stdlib “unsafe load” class (CWE-502) — distinct from pickle for taint path variety
    import marshal

    raw = base64.b64decode(merged_b64 or "", altchars=None, validate=False)  # noqa: S104
    obj = marshal.loads(raw)  # noqa: S301
    return repr(obj)[:2000]
