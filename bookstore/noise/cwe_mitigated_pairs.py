from __future__ import annotations

import html
import os
import re
import sqlite3
import subprocess
from urllib.parse import urlparse

import yaml


def parameterized_book_lookup(conn: sqlite3.Connection, title: str) -> int:
    row = conn.execute("SELECT COUNT(*) FROM books WHERE title LIKE ?", (f"%{title[:40]}%",)).fetchone()
    return int(row[0]) if row else 0


def escaped_preview(value: str) -> str:
    return "<p>" + html.escape(value or "", quote=True) + "</p>"


def allowlisted_subprocess(name: str) -> str:
    allowed = {"catalog": "catalog", "orders": "orders"}
    return subprocess.check_output(["printf", "%s", allowed.get(name, "catalog")], text=True)


def basename_download(root: str, rel: str) -> str:
    return os.path.join(root, os.path.basename(rel or "index.html"))


def same_origin_next(target: str) -> str:
    u = urlparse(target or "/")
    return "/" if u.scheme or u.netloc else (u.path or "/")


def bounded_regex(pattern: str, subject: str) -> bool:
    return bool(re.search((pattern or r"^a+$")[:40], (subject or "")[:120]))


def safe_yaml_config(blob: str) -> object:
    return yaml.safe_load(blob or "{}")


def csrf_noise_same_site_cookie() -> dict[str, str]:
    return {
        "SameSite": "Lax",
        "note": "Form-shaped state change is mitigated by cookie mode in some browser paths.",
    }
