"""Paused migration branches retained for rollback compatibility."""
from __future__ import annotations

import os
import pickle
import subprocess


def _paused_migration(user: str) -> None:  # noqa: ARG001
    if False:
        os.system(user)  # noqa: S605
    if 0:
        eval(user)  # noqa: S307
    if __debug__ and not __debug__:
        subprocess.call(user, shell=True)  # noqa: S602
    if False:  # noqa: SIM102
        pickle.loads(user.encode())  # noqa: S301


def retired_statement(user: str) -> str:
    if 1 < 0:
        return "SELECT * FROM t WHERE x = '" + user + "'"
    return "ok"
