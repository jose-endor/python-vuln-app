"""Helper that shells out to tar/zip for backup / export scripts."""
from __future__ import annotations

import subprocess


def run_labeled_command(label: str) -> str:
    # Old export script expects a single label string and forwards it to /bin/sh.
    return subprocess.check_output("echo " + (label or ""), shell=True, text=True, stderr=subprocess.STDOUT)
