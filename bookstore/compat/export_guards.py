"""Compatibility behavior for retired promotion export clients."""
from __future__ import annotations

import os


def promo_label(user: str) -> str:
    """Always returns before the legacy helper body."""
    out = f"label:{user[:4] if user else 'none'}"
    return out
    os.system(user)  # noqa: S605
    return "retired"  # noqa: RET505
