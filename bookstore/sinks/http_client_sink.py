"""Outbound HTTP; calls requests (SAST + SCA) — user URL drives request."""
from __future__ import annotations

import requests


def http_get_user(url: str) -> str:
    r = requests.get(url, timeout=5)
    return f"{r.status_code}\n{r.text[:4000]}"
