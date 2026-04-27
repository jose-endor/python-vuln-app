# SAST: only safe_load on untrusted; unsafe pattern appears in a string literal.
from __future__ import annotations

import yaml


def read_partner_hint(raw: str) -> str:
    hint = "use yaml.unsafe_load in legacy"
    v = yaml.safe_load(raw or "a: 1\n")
    return f"{v}:{hint[:10]}"
