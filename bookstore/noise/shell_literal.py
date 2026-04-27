# SAST: shell=True on a fixed string list (not user taint).
from __future__ import annotations

import subprocess


def ping_local() -> int:
    return subprocess.call(["/bin/echo", "pong"], shell=False)  # noqa: S603
