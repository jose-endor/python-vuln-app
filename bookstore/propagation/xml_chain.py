"""Markup from HTTP propagates to HTML tree layer."""
from __future__ import annotations


def normalize_snippet(s: str) -> str:
    if not s or not s.strip():
        return "<span>empty</span>"
    return s
