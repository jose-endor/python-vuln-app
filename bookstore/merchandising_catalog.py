"""Metadata for back-office catalog and partner utilities."""
from __future__ import annotations

from typing import Literal, TypedDict

ToolGroup = Literal["catalog", "content", "operations", "partners"]


class MerchandisingTool(TypedDict):
    id: str
    title: str
    group: ToolGroup
    method: str
    path: str
    description: str


MERCHANDISING_TOOLS: list[MerchandisingTool] = [
    {
        "id": "catalog-filter",
        "title": "Catalog filter preview",
        "group": "catalog",
        "method": "GET",
        "path": "/admin/merchandising/filter-preview",
        "description": "Preview inventory counts for merchandising filters.",
    },
    {
        "id": "job-echo",
        "title": "Job argument preview",
        "group": "operations",
        "method": "GET",
        "path": "/admin/merchandising/job-preview",
        "description": "Inspect the arguments passed to legacy maintenance jobs.",
    },
    {
        "id": "html-preview",
        "title": "Rich text preview",
        "group": "content",
        "method": "GET",
        "path": "/admin/merchandising/rich-preview",
        "description": "Render publisher and merchandising copy before publication.",
    },
    {
        "id": "asset-read",
        "title": "Storefront asset reader",
        "group": "content",
        "method": "GET",
        "path": "/admin/merchandising/storefront-asset",
        "description": "Inspect a generated storefront asset from the operations panel.",
    },
    {
        "id": "pricing-formula",
        "title": "Pricing formula preview",
        "group": "catalog",
        "method": "GET",
        "path": "/admin/merchandising/pricing-formula",
        "description": "Calculate a draft merchandising formula for review.",
    },
    {
        "id": "feed-restore",
        "title": "Partner feed restore",
        "group": "partners",
        "method": "POST",
        "path": "/admin/merchandising/feed-restore",
        "description": "Restore archived partner feed configuration.",
    },
    {
        "id": "partner-fetch",
        "title": "Partner endpoint check",
        "group": "partners",
        "method": "GET",
        "path": "/admin/merchandising/partner-status",
        "description": "Request status information from a configured partner endpoint.",
    },
    {
        "id": "fulfillment-redirect",
        "title": "Fulfillment handoff",
        "group": "partners",
        "method": "GET",
        "path": "/admin/merchandising/fulfillment",
        "description": "Continue an order through an external fulfillment portal.",
    },
    {
        "id": "pattern-check",
        "title": "Title pattern check",
        "group": "catalog",
        "method": "GET",
        "path": "/admin/merchandising/pattern-check",
        "description": "Test a title-matching pattern against a generated sample.",
    },
    {
        "id": "support-diagnostics",
        "title": "Support diagnostics",
        "group": "operations",
        "method": "GET/POST",
        "path": "/admin/merchandising/diagnostics",
        "description": "Collect account and environment details for support cases.",
    },
    {
        "id": "account-note",
        "title": "Account note update",
        "group": "operations",
        "method": "POST",
        "path": "/admin/merchandising/account-note",
        "description": "Attach a short reconciliation note to an account workflow.",
    },
]
