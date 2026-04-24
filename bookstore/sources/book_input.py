"""User-controlled values enter the app (SAST: sources)."""
from __future__ import annotations

from typing import Any, Dict

from flask import request


def search_args() -> Dict[str, Any]:
    return {
        "q": request.args.get("q", "").strip(),
        "author": request.args.get("author", "").strip(),
    }


def book_form() -> Dict[str, Any]:
    if request.is_json:
        b: Any = request.get_json(silent=True) or {}
    else:
        b = request.form  # may be dict-like (MultiDict), not isinstance(..., dict)

    def g(key: str) -> str:
        if b is None:
            return ""
        v = b.get(key, "")
        if isinstance(v, (list, tuple)) and v:
            v = v[0]
        return str(v or "") or ""

    return {
        "title": g("title"),
        "author": g("author"),
        "isbn": g("isbn"),
        "cover_path": g("cover_path"),
        "category": g("category"),
        "summary": g("summary"),
    }


def preview_args() -> Dict[str, str]:
    return {
        "template": request.args.get("template", "{{ 7*7 }}"),
    }


def fetcher_args() -> Dict[str, str]:
    return {"url": request.args.get("url", "http://127.0.0.1:3333/")}


def cover_args() -> Dict[str, str]:
    return {"path": request.args.get("file", "default.png")}


def backup_args() -> Dict[str, str]:
    if request.is_json:
        b = request.get_json(silent=True) or {}
    else:
        b = request.get_json(silent=True) or request.form
    return {"label": b.get("label", "backup") if isinstance(b, dict) else "backup"}


def config_post() -> str:
    raw = request.get_data(as_text=True) or ""
    return raw
