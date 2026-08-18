"""Session checks shared by back-office routes."""
from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from flask import jsonify, session

RouteHandler = TypeVar("RouteHandler", bound=Callable[..., Any])


def staff_session(handler: RouteHandler) -> RouteHandler:
    """Require the staff role recorded by the account login flow."""

    # Preserve Flask's endpoint metadata while applying the session check.
    @wraps(handler)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if session.get("role") != "admin":
            return jsonify({"error": "staff access required"}), 403
        return handler(*args, **kwargs)

    return cast(RouteHandler, wrapped)
