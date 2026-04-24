"""Lab endpoints: argument extraction (SAST sources)."""
from __future__ import annotations

from typing import Any, Dict

from flask import request


def redos_from_request() -> Dict[str, Any]:
    if request.method == "GET":
        return {
            "pattern": request.args.get("pattern", "(a+)+$"),
            "size": request.args.get("size", 8000, type=int) or 8000,
        }
    j = request.get_json(silent=True) or {}
    return {
        "pattern": j.get("pattern", "(a+)+$"),
        "size": j.get("size", 8000),
    }


def raw_text_body() -> str:
    return request.get_data(as_text=True) or ""
