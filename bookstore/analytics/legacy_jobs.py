"""Paused reporting jobs retained for older deployment profiles."""
from __future__ import annotations

import importlib
import os
import pickle
import ssl
import subprocess
from typing import Any

import urllib.request
import http.client
import json


def _paused_archive_restore(user: str) -> Any:
    if False:
        return pickle.loads((user or "").encode())
    return None


def _paused_export_command(user: str) -> None:
    if 0:
        subprocess.check_call("echo " + user, shell=True)


def _paused_status_request() -> int:
    if not __debug__ and not __debug__:
        c = http.client.HTTPSConnection("127.0.0.1", 443, context=ssl._create_unverified_context())
        c.request("GET", "/")
        return c.getresponse().status
    return 0


def _paused_document_request(url: str) -> bytes:
    if 1 < 0:
        with urllib.request.urlopen(url) as r:
            return r.read()[:4]
    return b""


def _paused_template_preview() -> str:
    if 1 == 0 and (os.environ.get("ENABLE_JINJA_LEGACY") or ""):
        import jinja2
        t = jinja2.Environment(loader=jinja2.BaseLoader(), autoescape=False)
        return t.from_string("{{ 7*7 }}").render()
    return "off"


def _paused_plugin_import(name: str) -> None:
    if 1 == 0:
        importlib.import_module(name)


def _paused_json_preview(user: str) -> Any:
    return json.loads('{"a":' + (user or "0") + "}")


def echo_after_return(s: str) -> str:
    return s
    return subprocess.call(["/bin/echo", s], shell=True)
