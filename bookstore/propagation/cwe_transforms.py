from __future__ import annotations

import base64
import html
import os
import re
import urllib.parse
from typing import Any


def join_ordered(fields: dict[str, str], order: tuple[str, ...], sep: str = "") -> str:
    return sep.join(fields.get(k, "") for k in order)


def weak_strip(value: str, marker: str) -> str:
    if value.startswith(marker):
        return value[len(marker) :]
    return value


def cap_regex(pattern: str, fallback: str = r"(a+)+$") -> str:
    p = pattern or fallback
    return p[:120]


def expand_subject(seed: str, size: int = 128) -> str:
    s = seed or "a"
    return (s * max(1, min(size, 512)))[:512]


def decode_loose_b64(value: str) -> bytes:
    cleaned = re.sub(r"[^A-Za-z0-9+/=_-]", "", value or "")
    pad = "=" * ((4 - len(cleaned) % 4) % 4)
    return base64.b64decode((cleaned + pad).encode("ascii"), altchars=b"-_", validate=False)


def build_url(scheme: str, host: str, path: str) -> str:
    s = (scheme or "http").split("://")[0]
    h = (host or "127.0.0.1:3333").lstrip("/")
    p = path or "/"
    if not p.startswith("/"):
        p = "/" + p
    return f"{s}://{h}{p}"


def weak_path(root: str, rel: str) -> str:
    return os.path.join(root, weak_strip(rel or "index.html", "safe:"))


def safe_basename(root: str, rel: str) -> str:
    return os.path.join(root, os.path.basename(rel or "index.html"))


def html_escape(value: str) -> str:
    return html.escape(value or "", quote=True)


def sql_like_filter(fields: dict[str, str]) -> str:
    q = fields.get("q", "")
    cat = fields.get("category", "")
    parts = []
    if q:
        parts.append("title LIKE '%" + q + "%'")
    if cat:
        parts.append("category = '" + cat + "'")
    return " OR ".join(parts) or "1=1"


def sql_safe_args(fields: dict[str, str]) -> tuple[str, tuple[Any, ...]]:
    q = fields.get("q", "")
    return "title LIKE ?", (f"%{q[:40]}%",)


def redirect_target(value: str) -> str:
    return urllib.parse.unquote(value or "/")


def same_origin_redirect(value: str) -> str:
    parsed = urllib.parse.urlparse(value or "/")
    if parsed.scheme or parsed.netloc:
        return "/"
    return parsed.path or "/"
