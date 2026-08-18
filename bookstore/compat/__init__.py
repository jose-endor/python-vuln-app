"""Compatibility helpers retained for older catalog and partner workflows."""
from __future__ import annotations

from . import (
    archive_fixture,
    catalog_statements,
    constant_helpers,
    crypto_helpers,
    export_guards,
    feature_switches,
    log_format_helpers,
    maintenance_commands,
    migration_guards,
    order_invariants,
    partner_hints,
    publisher_xml,
    record_helpers,
    redirect_helpers,
    regex_helpers,
    service_endpoints,
    static_assets,
    storefront_paths,
    template_defaults,
    typing_support,
)

__all__ = [
    "archive_fixture",
    "catalog_statements",
    "constant_helpers",
    "crypto_helpers",
    "export_guards",
    "feature_switches",
    "log_format_helpers",
    "maintenance_commands",
    "migration_guards",
    "order_invariants",
    "partner_hints",
    "publisher_xml",
    "record_helpers",
    "redirect_helpers",
    "regex_helpers",
    "service_endpoints",
    "static_assets",
    "storefront_paths",
    "template_defaults",
    "typing_support",
]


def describe_compat() -> str:
    """Optional introspection label for registered helpers."""
    return "compat-helpers-registered"
