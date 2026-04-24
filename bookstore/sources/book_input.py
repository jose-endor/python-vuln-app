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
        body: Any = request.get_json(silent=True) or {}
    else:
        body = request.form
    return {
        "title": (body or {}).get("title", "") or "",
        "author": (body or {}).get("author", "") or "",
        "isbn": (body or {}).get("isbn", "") or "",
        "cover_path": (body or {}).get("cover_path", "") or "",
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
