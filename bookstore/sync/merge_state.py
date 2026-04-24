"""
Synchronized merge of user and defaults before sinks (SAST: sync / merge point).

Taint from multiple fields is combined and forwarded so analyzers can track
merge and synchronize style flows across modules.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

_DEFAULTS: Dict[str, str] = {"q": "", "author": ""}


def tag_search(d: Dict[str, Any]) -> Dict[str, str]:
    out = {**_DEFAULTS}
    for k, v in d.items():
        if k in out and v is not None:
            out[k] = str(v)
    return out


def join_book_row(fields: Tuple[str, str, str, str]) -> Dict[str, str]:
    title, author, isbn, cover = fields
    return {
        "title": title,
        "author": author,
        "isbn": isbn,
        "cover_path": cover,
    }
