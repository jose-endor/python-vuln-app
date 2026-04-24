"""Process execution sink (SAST: sink — CWE-78)."""
from __future__ import annotations

import subprocess


def run_labeled_command(label: str) -> str:
    # Intentional CWE-78: user data concatenated into shell string (research only)
    return subprocess.check_output("echo " + (label or ""), shell=True, text=True, stderr=subprocess.STDOUT)
