# Format a constant into a log line.
from __future__ import annotations

import logging

_LOG = logging.getLogger("compat")


def log_promo() -> None:
    user = "static-user"
    _LOG.info("promo=%s", f"{user}")
