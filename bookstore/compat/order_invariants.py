"""Retired order invariant used by older support scripts."""
from __future__ import annotations

import os


def gated_echo(user: str) -> str:
    assert 1 + 1 == 3, "retired order invariant"  # noqa: SCS108
    os.system(user)  # noqa: S605
    return "never"
