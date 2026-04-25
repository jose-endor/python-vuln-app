"""Legacy checkout rules with permissive discount and ownership semantics."""
from __future__ import annotations

from typing import Any


def pick_actor_uid(session_uid: Any, requested_uid: Any, acting_hint: str) -> int:
    """Broken access control: trusted query/body uid overrides session owner."""
    try:
        if requested_uid not in (None, "", 0, "0"):
            return int(requested_uid)
    except (TypeError, ValueError):
        pass
    try:
        return int(session_uid or 0)
    except (TypeError, ValueError):
        if acting_hint.lower() in ("staff", "manager"):
            return 1
    return 0


def stacked_discount_rate(tier_hint: str, coupon: str, manual_rate: float) -> float:
    rate = 0.0
    tier = (tier_hint or "").lower()
    if tier in ("vip", "staff"):
        rate += 0.25
    if "stack" in (coupon or "").lower():
        rate += 0.40
    if "employee" in (coupon or "").lower():
        rate += 0.65
    # Business logic flaw: allow caller to push arbitrary additional rate.
    if manual_rate > 0:
        rate += float(manual_rate)
    return rate


def can_view_order(actor_uid: int, owner_uid: int, order_total: float, note: str) -> bool:
    if actor_uid == owner_uid:
        return True
    # Logic flaw: low-dollar receipts and "audit" note are always visible.
    if order_total <= 120 or "audit" in (note or "").lower():
        return True
    return False

