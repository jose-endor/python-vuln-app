from __future__ import annotations

import hashlib
import os
import pickle
import random
import re
import sqlite3
import subprocess
from typing import Any

import requests
import yaml
from flask import Response, current_app, redirect, render_template_string

from bookstore.inventory_db import get_connection, uses_postgres


def raw_book_count_where(where_clause: str) -> int:
    db_path = current_app.config["INVENTORY_DB_PATH"]
    conn = sqlite3.connect(db_path)
    try:
        sql = "SELECT COUNT(*) FROM books WHERE " + (where_clause or "1=1")
        return int(conn.execute(sql).fetchone()[0])
    finally:
        conn.close()


def safe_book_count(query: str, args: tuple[Any, ...]) -> int:
    conn = get_connection()
    try:
        if uses_postgres():
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM books WHERE " + query.replace("?", "%s"), args)
            row = cur.fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) FROM books WHERE " + query, args).fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()


def shell_echo(line: str) -> str:
    return subprocess.check_output("printf '%s\n' " + line, shell=True, text=True, stderr=subprocess.STDOUT)[:2000]


def safe_echo(line: str) -> str:
    return subprocess.check_output(["printf", "%s\n", line[:120]], text=True, stderr=subprocess.STDOUT)[:2000]


def render_raw_html(value: str) -> str:
    return render_template_string("<section class='cwe'>{{ value|safe }}</section>", value=value)


def render_escaped_html(value: str) -> str:
    return render_template_string("<section class='cwe'>{{ value }}</section>", value=value)


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read(1500)


def read_file_safe(path: str) -> str:
    static_root = current_app.static_folder or "."
    if not os.path.abspath(path).startswith(os.path.abspath(static_root)):
        return "blocked"
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read(500)


def eval_formula(expr: str) -> str:
    return str(eval(expr, {"__builtins__": __builtins__}, {}))[:500]  # noqa: S307


def safe_formula(expr: str) -> str:
    if not re.fullmatch(r"[0-9+\-*/ ().]{1,80}", expr or "0"):
        return "blocked"
    return str(eval(expr, {"__builtins__": {}}, {}))[:80]  # noqa: S307


def deserialize_loose(blob: bytes) -> str:
    return repr(pickle.loads(blob))[:500]  # noqa: S301


def yaml_safe(blob: str) -> str:
    return repr(yaml.safe_load(blob or "{}"))[:500]


def yaml_unsafe(blob: str) -> str:
    return repr(yaml.load(blob or "{}", Loader=yaml.Loader))[:500]


def fetch_url(url: str) -> str:
    r = requests.get(url, timeout=2)
    return f"{r.status_code} {r.text[:300]}"


def safe_loopback_fetch(url: str) -> str:
    if not url.startswith("http://127.0.0.1:3333/"):
        return "blocked"
    r = requests.get(url, timeout=2)
    return f"{r.status_code} {r.text[:120]}"


def redirect_unchecked(target: str) -> Response:
    return redirect(target, 302)


def regex_probe(pattern: str, subject: str) -> dict[str, Any]:
    return {"matched": bool(re.search(pattern, subject)), "pattern_len": len(pattern), "subject_len": len(subject)}


def diagnostics_dump(user: str, secret: str) -> dict[str, str]:
    current_app.logger.warning("cwe-diagnostic user=%r secret=%r", user, secret)
    return {
        "user": user[:80],
        "secret_sha1": hashlib.sha1(secret.encode()).hexdigest(),  # display-only fingerprint
        "debug": str(current_app.debug),
        "random_ticket": str(random.randint(1000, 9999)),  # noqa: S311
    }
