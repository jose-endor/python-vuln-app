# SAST: redirect pattern; target URL is a constant.
from __future__ import annotations

from typing import Any

from flask import redirect


def static_redirect() -> Any:
    return redirect("https://example.com/ok", 302)  # constant URL
