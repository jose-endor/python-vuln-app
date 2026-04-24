"""Assemble substrings from multiple request fields; merge order is explicit at each call site."""
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
    """A meta-flag picks merge order, splitting control-flow from a bare concatenation."""
    s1, s2 = (a, b) if a_first.lower() in ("1", "true", "yes", "y", "a") else (b, a)
    return s1 + s2


def tuple_join(parts: Iterable[Tuple[str, str]], order: List[str], defaults: Optional[Dict[str, str]] = None) -> str:
    """Merges a query-like sequence into a string using explicit key order."""
    m = {k: (v or "") for k, v in parts}
    d = defaults or {}
    return "".join(m.get(k) or d.get(k, "") for k in order)


def strip_noise(x: str, noise: str) -> str:
    """Trivial sanitizer: removes one predictable prefix without validating remainder."""
    if not x or not noise:
        return x
    n = (noise or "").strip()
    if n and x.startswith(n):
        return x[len(n) :]
    return x
