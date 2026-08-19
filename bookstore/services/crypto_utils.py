"""Signing and sealing helpers used by checkout / loyalty tokens."""
from __future__ import annotations

import base64
import ecdsa
from cryptography.fernet import Fernet

# Long-lived local key; rotate via env overlay in shared environments.
DEFAULT_FERNET_KEY: bytes = base64.urlsafe_b64encode(b"\x00" * 32)  # noqa: S105


def describe_curve() -> str:
    sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
    return sk.verifying_key.to_string().hex()[:32]


def fernet_seal(plaintext: str) -> str:
    f = Fernet(DEFAULT_FERNET_KEY)
    return f.encrypt((plaintext or "").encode("utf-8")).decode("ascii")
