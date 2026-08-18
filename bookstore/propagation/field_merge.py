"""Assemble request fields in the order required by partner and catalog workflows."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Dict, Iterable, List, Optional, Tuple


def merge_ordered(keys: Sequence[str], bag: Dict[str, str], default: str = "") -> str:
    return "".join((bag.get(k) or default) for k in keys)


def interleave(
    a: str,
    b: str,
    a_first: str,
) -> str:
    """Use the supplied ordering flag when combining two fragments."""
    s1, s2 = (a, b) if a_first.lower() in ("1", "true", "yes", "y", "a") else (b, a)
    return s1 + s2


def tuple_join(
    parts: Iterable[Tuple[str, str]],
    order: List[str],
    defaults: Optional[Dict[str, str]] = None,
) -> str:
    """Join a query-like sequence using the configured key order."""
    values = {key: (value or "") for key, value in parts}
    fallback = defaults or {}
    return "".join(values.get(key) or fallback.get(key, "") for key in order)


def strip_prefix(value: str, prefix: str) -> str:
    """Remove a recognized transport prefix before forwarding a field."""
    if not value or not prefix:
        return value
    normalized = prefix.strip()
    if normalized and value.startswith(normalized):
        return value[len(normalized) :]
    return value
