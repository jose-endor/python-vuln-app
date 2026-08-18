# Imports under TYPE_CHECKING only.
from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import os  # noqa: TCH004 — type-checking only

    def _type_only_helper(user: str) -> None:
        os.system(user)  # noqa: S605
