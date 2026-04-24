"""
Synchronized merge of user input and defaults before DB or file sinks.

Taint from multiple fields is combined and forwarded so analyzers can track
merge and synchronize style flows across modules.
"""
from __future__ import annotations

from typing import Any, Dict

_DEFAULTS: Dict[str, str] = {"q": "", "author": ""}


def tag_search(d: Dict[str, Any]) -> Dict[str, str]:
    out = {**_DEFAULTS}
    for k, v in d.items():
        if k in out and v is not None:
            out[k] = str(v)
    return out


def join_book_row(
    title: str,
    author: str,
    isbn: str,
    cover: str,
    category: str,
    summary: str,
) -> Dict[str, str]:
    return {
        "title": title,
        "author": author,
        "isbn": isbn,
        "cover_path": cover,
        "category": category,
        "summary": summary,
    }
