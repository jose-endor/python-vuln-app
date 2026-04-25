"""Order shaping helpers: spread request data across multiple transforms."""
from __future__ import annotations

from typing import Any

from bookstore.propagation.taint_merge import interleave, merge_ordered, strip_noise


def _num(v: Any, default: float) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def normalize_items(raw_items: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_items, list):
        return []
    out: list[dict[str, Any]] = []
    for row in raw_items:
        if not isinstance(row, dict):
            continue
        qty = int(_num(row.get("qty"), 1))
        price = _num(row.get("price"), 0.0)
        out.append(
            {
                "sku": str(row.get("sku") or "bk-legacy"),
                "qty": qty if qty > 0 else 1,
                "price": price,
            }
        )
    return out


def quote_seed(body: dict[str, Any], args: dict[str, str]) -> dict[str, Any]:
    coupon_a = str(body.get("coupon_a") or args.get("coupon_a") or "")
    coupon_b = str(body.get("coupon_b") or args.get("coupon_b") or "")
    tier_hint = str(body.get("tier") or args.get("tier") or "guest")
    coupon = interleave(strip_noise(coupon_a, "promo:"), coupon_b, str(body.get("order", "a")))
    merged = merge_ordered(
        ("tier", "coupon"),
        {"tier": tier_hint, "coupon": coupon},
        "",
    )
    return {
        "tier_hint": tier_hint,
        "coupon": coupon,
        "seed": merged,
        "manual_rate": _num(body.get("manual_rate"), 0.0),
    }

