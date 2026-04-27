# Mid/low-severity SAST pattern corpus; no routes; many findings are inert or unreachable.
from __future__ import annotations

from . import low_severity_bag, medium_severity_bag, mixed_lookalikes

__all__ = ["low_severity_bag", "medium_severity_bag", "mixed_lookalikes"]


def ping() -> str:
    return "sast-tiered-ok"
