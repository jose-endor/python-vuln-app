"""URL value propagates for outbound HTTP (SAST: propagation)."""
from __future__ import annotations

from urllib.parse import urlparse


def normalize_incoming_url(url: str) -> str:
    u = (url or "").strip()
    p = urlparse(u)
    if p.scheme in ("http", "https", ""):
        if not p.scheme:
            return "http://" + u
        return u
    return "http://127.0.0.1/"
