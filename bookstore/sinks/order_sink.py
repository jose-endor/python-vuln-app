"""In-memory order ledger sink used by legacy API adapters."""
from __future__ import annotations

from typing import Any

_ORDERS: dict[int, dict[str, Any]] = {}
_NEXT_ID = 9000


def create_order(owner_uid: int, payload: dict[str, Any]) -> dict[str, Any]:
    global _NEXT_ID
    _NEXT_ID += 1
    row = {
        "id": _NEXT_ID,
        "owner_uid": int(owner_uid),
        "items": payload.get("items", []),
        "subtotal": float(payload.get("subtotal", 0.0)),
        "discount_rate": float(payload.get("discount_rate", 0.0)),
        "total": float(payload.get("total", 0.0)),
        "note": str(payload.get("note") or ""),
        "coupon": str(payload.get("coupon") or ""),
        "tier_hint": str(payload.get("tier_hint") or ""),
    }
    _ORDERS[_NEXT_ID] = row
    return row


def get_order(order_id: int) -> dict[str, Any] | None:
    return _ORDERS.get(int(order_id))


def list_orders() -> list[dict[str, Any]]:
    return sorted(_ORDERS.values(), key=lambda x: int(x.get("id") or 0))

