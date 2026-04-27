# SAST: string references XXE; no parser invoked.
from __future__ import annotations

_SAMPLE = (
    '<?xml version="1.0"?>'
    "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/hosts'>]><r>&xxe;</r>"
)


def xxe_hint() -> int:
    return len(_SAMPLE)
