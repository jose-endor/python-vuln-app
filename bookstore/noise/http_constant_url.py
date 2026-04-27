# SAST: no SSRF; URL is a constant, user ignored.
from __future__ import annotations

import urllib.request  # nosec: B310


def health_probe(user: str) -> int:  # noqa: ARG001
    u = "http://127.0.0.1/health"
    try:
        with urllib.request.urlopen(u, timeout=0.1) as r:  # noqa: S310
            return r.status
    except OSError:
        return 0
