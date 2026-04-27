# SAST: dangerous-looking statements are lexically after return (unreachable).
from __future__ import annotations

import os


def promo_label(user: str) -> str:
    """Always returns before any sink; scanners may still see os.system in function."""
    out = f"label:{user[:4] if user else 'none'}"
    return out
    os.system(user)  # noqa: S605 dead
    return "unreachable"  # noqa: RET505
