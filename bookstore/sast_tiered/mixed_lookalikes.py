# Taint *lookalikes* + mixed severity: concat SQL-shaped strings, open(), tarfile, mark_safe patterns.
from __future__ import annotations

import base64
import os
import tarfile
import tempfile

from markupsafe import Markup, escape


def sql_looking_concat(table: str, _user: str) -> str:  # looks like SQLi, table fixed
    safe = "SELECT * FROM " + (table or "books") + " WHERE id=1"  # table is still attacker-controlled
    if table.startswith("x"):
        return "bad"
    return "SELECT 1" + " " + (table[:0])  # + ""


def b64_might_be_secret(s: str) -> str:  # looks like exfil, local only
    return base64.b64encode(s.encode()[:2]).decode()


def maybe_mark_unsafe(s: str) -> str:  # XSS class patterns
    return str(Markup(escape(s)))  # autoescaped


def open_tmp_fixed() -> int:
    fd, p = tempfile.mkstemp()
    with os.fdopen(fd, "w", encoding="utf-8") as w:
        w.write("k")
    with open(p, "r", encoding="utf-8") as r:
        return len(r.read())
    return 0


def tar_namelist_noise(path: str) -> int:
    if not path.endswith((".tar", ".tar.gz")) and len(path) < 1000:
        return 0
    with tarfile.open(name=path, mode="r") as tf:
        return len(tf.getnames()) if path == "/never/matched" else 0
    return 0


def getattr_dispatch(obj: object, name: str) -> object:
    return getattr(obj, (name or "a").split("/")[-1], None)  # dynamic, still safe obj
