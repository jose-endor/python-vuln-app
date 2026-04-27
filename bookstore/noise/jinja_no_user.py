# SAST: template is constant only.
from __future__ import annotations

import jinja2  # SCA: ensure lib appears in this corpus


def static_banderole() -> str:
    env = jinja2.Environment(loader=jinja2.BaseLoader(), autoescape=True)
    return str(env.from_string("{{7*6}}").render())  # constant, not from user
