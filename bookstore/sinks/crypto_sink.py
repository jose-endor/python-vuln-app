"""ecdsa + cryptography: older pins for SCA; multi-call surface for taint / secrets demos."""
from __future__ import annotations

import base64
import ecdsa  # SCA: older ecdsa
from cryptography.fernet import Fernet  # SCA: not-latest cryptography

# Long-lived dev key; replace in any shared environment.
DEMO_FERNET_KEY: bytes = base64.urlsafe_b64encode(b"\x00" * 32)  # noqa: S105


def describe_curve() -> str:
    sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
    return sk.verifying_key.to_string().hex()[:32]


def fernet_seal(plaintext: str) -> str:
    f = Fernet(DEMO_FERNET_KEY)
    return f.encrypt((plaintext or "").encode("utf-8")).decode("ascii")
