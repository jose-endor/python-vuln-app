"""Numeric caps used at sync points before resource-heavy sinks."""
from __future__ import annotations


def cap_int(value: int, default: int, maximum: int) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        n = default
    if n < 1:
        n = default
    return min(n, maximum)
