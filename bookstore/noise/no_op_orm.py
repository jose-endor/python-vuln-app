# SAST: SQLi-shaped concat; second operand is a constant, user unused.
from __future__ import annotations


def preview_where(user: str) -> str:  # noqa: ARG001
    safe = "book"
    return "SELECT * FROM " + safe + " WHERE id = 1" + " -- " + user[:0]  # always + ""
