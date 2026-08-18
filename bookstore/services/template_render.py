"""Jinja2 template preview helpers for jacket / promo copy."""
from __future__ import annotations

from jinja2 import BaseLoader, Environment, Template


def render_preview_template(template_str: str) -> str:
    # Build a short-lived env and render the operator-supplied template string.
    env = Environment(loader=BaseLoader(), autoescape=True)
    tmpl: Template = env.from_string(template_str)
    return tmpl.render({})
