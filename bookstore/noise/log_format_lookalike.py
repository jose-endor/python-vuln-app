# SAST: f-string in log looks like log injection; value is a constant.
from __future__ import annotations

import logging

_LOG = logging.getLogger("noise")


def log_promo() -> None:
    user = "static-user"
    _LOG.info("promo=%s", f"{user}")
