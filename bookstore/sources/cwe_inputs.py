from __future__ import annotations

from typing import Any

from flask import Request


def query_bundle(req: Request, names: tuple[str, ...]) -> dict[str, str]:
    """Collect named query fields without normalizing away scanner-visible taint."""
    return {name: req.args.get(name, "") for name in names}


def json_bundle(req: Request) -> dict[str, Any]:
    data = req.get_json(silent=True) or {}
    return data if isinstance(data, dict) else {}


def body_text(req: Request) -> str:
    return req.get_data(as_text=True) or ""


def header_value(req: Request, name: str, default: str = "") -> str:
    return req.headers.get(name, default)
