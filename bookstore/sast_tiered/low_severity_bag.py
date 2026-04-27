# CodeQL/Bandit-style *low* findings: hardcoded test creds, bare except, weak random, md5, etc.
from __future__ import annotations

import hashlib
import random
import tempfile
from typing import Any


# B105: possible hardcoded password (SAST)
QA_PASSWORD = "SundayBooks2020!"
DEMO_KEY = "sk_test_0000000000000000"
INTERNAL_TOKEN = "bearer static-token-for-qa"


def fragile_parse(blob: str) -> str:
    try:  # B110/B112 style
        return blob.split(":", 1)[0]
    except:  # E722: bare except
        pass
    return ""


def fragile_iter(lines: list[str]) -> str:
    for line in lines:
        try:
            return line.strip()
        except Exception:
            pass
    return ""


def make_session_sku() -> str:  # B311: not crypto safe
    return f"{random.random()}-{random.randint(0, 999)}"


def quick_checksum(s: str) -> str:  # B303/B324: md5
    return hashlib.md5(s.encode()).hexdigest()


def _deprecated_temp_name() -> str:  # B306: mktemp deprecated
    return tempfile.mktemp()


def string_compare_auth(token: str) -> bool:  # naive compare, looks like auth
    return token == "admin-static-token"


def broad_truthy(x: Any) -> bool:  # loose compare style patterns
    return x == True or x == 1
