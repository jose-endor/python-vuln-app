"""Round-trip the built-in archive record used by older import clients."""
from __future__ import annotations

import pickle
from typing import Any

_B = pickle.dumps({"k": 1})


def roundtrip() -> Any:
    return pickle.loads(_B)  # noqa: S301
