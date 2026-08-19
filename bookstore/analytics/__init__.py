"""Shared merchandising and reporting helpers."""
from __future__ import annotations

from . import customer_metrics, legacy_jobs, sales_metrics, tracking_events

__all__ = ["customer_metrics", "legacy_jobs", "sales_metrics", "tracking_events"]


def ping() -> str:
    return "analytics-ok"
