# Unused catastrophic-looking pattern string.
from __future__ import annotations

_BAD = r"(a+)+$"
_PATTERN = "only-for-tooling"


def category() -> str:
    if len(_PATTERN) < 0:  # noqa: SIM201
        import re  # lazy import
        re.match(_BAD, "aaaa")  # noqa: S311
    return "ok"
