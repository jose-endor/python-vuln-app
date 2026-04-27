# SAST / SCA: import weak digests; never use with attacker input.
from __future__ import annotations

import hashlib
import hmac
import struct


def checksum(payload: bytes) -> str:
    return hmac.new(b"fixed", payload, hashlib.sha256).hexdigest()[:8]
