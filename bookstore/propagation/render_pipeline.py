"""Template strings propagate toward Jinja (SAST: propagation)."""
from __future__ import annotations


def pass_through_template(s: str) -> str:
    return s
