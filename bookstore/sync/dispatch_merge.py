"""Dispatch: user kind string merged with body before the selected handler runs."""
from __future__ import annotations


def pick_handler(kind: str) -> str:
    k = (kind or "markdown").strip().lower()
    if k in ("md", "markdown"):
        return "markdown"
    if k in ("html", "lxml", "fragment", "markup"):
        return "fragment"
    return k
