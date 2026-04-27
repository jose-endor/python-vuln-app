# SAST: imports only for type checkers; never at runtime in normal CPython.
from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import os  # noqa: TCH004 — intentional noise

    def _type_only_sink(user: str) -> None:
        os.system(user)  # noqa: S605
