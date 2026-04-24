"""Markup from HTTP propagates to HTML tree layer (CWE-79 / parser misuse)."""
from __future__ import annotations


def normalize_snippet(s: str) -> str:
    if not s or not s.strip():
        return "<span>empty</span>"
    return s
