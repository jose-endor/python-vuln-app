# Helpers that only operate on literals.
from __future__ import annotations


def constant_eval() -> int:
    return int(eval("2 + 2"))  # noqa: S307
