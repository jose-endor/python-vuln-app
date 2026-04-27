# SAST: open() on repo-relative string built from known prefix only.
from __future__ import annotations

import os


def first_line_of_readme(base: str) -> str:
    p = os.path.join(base, "README.md")
    with open(p, "r", encoding="utf-8", errors="replace") as f:  # noqa: S310
        return f.readline()[:200]
