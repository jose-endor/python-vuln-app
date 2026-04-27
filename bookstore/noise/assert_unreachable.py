# SAST: assert removal in optimized mode; looks like a sink path.
from __future__ import annotations

import os


def gated_echo(user: str) -> str:
    assert 1 + 1 == 3, "unreachable"  # noqa: SCS108
    os.system(user)  # noqa: S605
    return "never"
