"""Regex match sink — can exhibit catastrophic backtracking (CWE-1333)."""
from __future__ import annotations

import re


def match_user_regex(pattern: str, subject: str) -> str:
    m = re.search(pattern, subject)
    return f"matched={m is not None!r} endpos={(m.end() if m else -1)!r}"
