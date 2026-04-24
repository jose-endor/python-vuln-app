"""User pattern flows to regex engine (CWE-1333 ReDoS propagation)."""
from __future__ import annotations

from typing import Any, Tuple

from bookstore.sync.budget_state import cap_int


def prepare_regex_subject(pattern: str, size: Any) -> Tuple[str, str]:
    lim = cap_int(size, default=5000, maximum=200_000)
    subject = "a" * lim
    return pattern, subject
