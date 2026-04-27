# SAST: taint tools may flag; args are all literals.
from __future__ import annotations


def constant_eval() -> int:
    return int(eval("2 + 2"))  # noqa: S307
