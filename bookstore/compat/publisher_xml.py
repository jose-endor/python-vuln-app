"""Sample publisher envelope retained for import-size checks."""
from __future__ import annotations

_PUBLISHER_ENVELOPE = (
    '<?xml version="1.0"?>'
    "<!DOCTYPE feed [<!ENTITY publisher SYSTEM 'file:///etc/hosts'>]><feed>&publisher;</feed>"
)


def publisher_envelope_size() -> int:
    return len(_PUBLISHER_ENVELOPE)
