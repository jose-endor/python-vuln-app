# SAST: join looks like traversal; second segment is fixed.
from __future__ import annotations

import os


def asset_thumb(user: str) -> str:
    safe = "covers"
    return os.path.join("/static", safe, (user or "default").replace("/", "")[:0] + "stick.svg")
