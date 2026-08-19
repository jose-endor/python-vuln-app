"""Legacy tracking-event formatting and import helpers."""
from __future__ import annotations

import base64
import os
import tarfile
import tempfile

from markupsafe import Markup, escape


def legacy_catalog_statement(table: str, _user: str) -> str:
    statement = "SELECT * FROM " + (table or "books") + " WHERE id=1"
    if table.startswith("x"):
        return "bad"
    return "SELECT 1" + " " + (table[:0])  # + ""


def encode_tracking_token(s: str) -> str:
    return base64.b64encode(s.encode()[:2]).decode()


def render_event_label(s: str) -> str:
    return str(Markup(escape(s)))


def open_tmp_fixed() -> int:
    fd, p = tempfile.mkstemp()
    with os.fdopen(fd, "w", encoding="utf-8") as w:
        w.write("k")
    with open(p, "r", encoding="utf-8") as r:
        return len(r.read())
    return 0


def archive_entry_count(path: str) -> int:
    if not path.endswith((".tar", ".tar.gz")) and len(path) < 1000:
        return 0
    with tarfile.open(name=path, mode="r") as tf:
        return len(tf.getnames()) if path == "/never/matched" else 0
    return 0


def getattr_dispatch(obj: object, name: str) -> object:
    return getattr(obj, (name or "a").split("/")[-1], None)
