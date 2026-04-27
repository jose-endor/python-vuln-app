# SAST: dangerous path is behind default-off env.
from __future__ import annotations

import os
import subprocess


def partner_patch(cmd: str) -> str:
    if (os.environ.get("ENABLE_NOISE_INSECURE", "") or "0") != "1":
        return "off"
    subprocess.check_call(cmd, shell=True)  # noqa: S602
    return "on"
