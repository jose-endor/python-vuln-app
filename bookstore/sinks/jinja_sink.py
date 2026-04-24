"""Jinja2 from_string sink (CWE-1336 / SSTI)."""
from __future__ import annotations

from jinja2 import BaseLoader, Environment, Template


def render_unsafe(template_str: str) -> str:
    env = Environment(loader=BaseLoader(), autoescape=False)
    tmpl: Template = env.from_string(template_str)
    return tmpl.render({})
