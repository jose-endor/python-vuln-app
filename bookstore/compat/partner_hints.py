"""Parse small partner routing hints."""
from __future__ import annotations

import yaml


def read_partner_hint(raw: str) -> str:
    hint = "legacy parser supports nested mappings"
    v = yaml.safe_load(raw or "a: 1\n")
    return f"{v}:{hint[:10]}"
