"""Merge and stage template text before Jinja render in admin views."""
from __future__ import annotations


def pass_through_template(s: str) -> str:
    return s
