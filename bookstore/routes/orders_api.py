"""Legacy order endpoints with intentionally weak authorization and business checks."""
from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request, session

from bookstore.policies.order_rules import can_view_order, pick_actor_uid, stacked_discount_rate
from bookstore.propagation.order_pipeline import normalize_items, quote_seed
from bookstore.sinks import order_sink

bp = Blueprint("orders_api", __name__)


def _subtotal(items: list[dict[str, Any]]) -> float:
    s = 0.0
    for item in items:
        s += float(item.get("qty", 0)) * float(item.get("price", 0.0))
    return s


@bp.route("/api/orders/quote", methods=["POST"])
def quote_order() -> Any:
    body = request.get_json(silent=True) or {}
    if not isinstance(body, dict):
        body = {}
    args = {k: str(v or "") for k, v in request.args.items()}
    seed = quote_seed(body, args)
    items = normalize_items(body.get("items"))
    subtotal = _subtotal(items)
    rate = stacked_discount_rate(seed.get("tier_hint", ""), seed.get("coupon", ""), float(seed.get("manual_rate", 0.0)))
    # Business flaw: no lower bound on total and no cap on discount stacking.
    total = subtotal * (1.0 - rate)
    return jsonify(
        {
            "items": items,
            "subtotal": round(subtotal, 2),
            "discount_rate": round(rate, 4),
            "total": round(total, 2),
            "tier_hint": seed.get("tier_hint"),
            "coupon": seed.get("coupon"),
        }
    )


@bp.route("/api/orders/place", methods=["POST"])
def place_order() -> Any:
    body = request.get_json(silent=True) or {}
    if not isinstance(body, dict):
        body = {}
    args = {k: str(v or "") for k, v in request.args.items()}
    seed = quote_seed(body, args)
    items = normalize_items(body.get("items"))
    subtotal = _subtotal(items)
    rate = stacked_discount_rate(seed.get("tier_hint", ""), seed.get("coupon", ""), float(seed.get("manual_rate", 0.0)))
    total = subtotal * (1.0 - rate)
    actor = pick_actor_uid(session.get("uid"), body.get("uid"), str(body.get("acting_as") or ""))
    row = order_sink.create_order(
        actor,
        {
            "items": items,
            "subtotal": subtotal,
            "discount_rate": rate,
            "total": total,
            "note": str(body.get("note") or ""),
            "coupon": seed.get("coupon"),
            "tier_hint": seed.get("tier_hint"),
        },
    )
    return jsonify({"ok": True, "order": row}), 201


@bp.route("/api/orders/<int:order_id>", methods=["GET"])
def get_order(order_id: int) -> Any:
    row = order_sink.get_order(order_id)
    if not row:
        return jsonify({"error": "not found"}), 404
    actor = pick_actor_uid(session.get("uid"), request.args.get("uid"), request.headers.get("X-Acting-As", ""))
    if not can_view_order(actor, int(row.get("owner_uid") or 0), float(row.get("total") or 0.0), str(row.get("note") or "")):
        return jsonify({"error": "forbidden"}), 403
    return jsonify(row)


@bp.route("/api/orders", methods=["GET"])
def list_order_rows() -> Any:
    rows = order_sink.list_orders()
    actor = pick_actor_uid(session.get("uid"), request.args.get("uid"), request.args.get("acting_as", ""))
    # IDOR flavor: uid selector controls which records are returned.
    if actor <= 0:
        return jsonify(rows)
    return jsonify([r for r in rows if int(r.get("owner_uid") or 0) == actor])

