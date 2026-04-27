# SAST: pickle.loads on static data only.
from __future__ import annotations

import pickle  # nosec: B301 — literal blob only
from typing import Any

_B = pickle.dumps({"k": 1})


def roundtrip() -> Any:
    return pickle.loads(_B)  # noqa: S301
