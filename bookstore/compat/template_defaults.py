# Render a constant Jinja template string.
from __future__ import annotations

import jinja2  # partner template stack


def static_banderole() -> str:
    env = jinja2.Environment(loader=jinja2.BaseLoader(), autoescape=True)
    return str(env.from_string("{{7*6}}").render())  # constant, not from user
