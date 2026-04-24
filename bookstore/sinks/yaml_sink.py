"""YAML load path for admin ingest; prefer safe_load in new code paths."""
from __future__ import annotations

import yaml  # SCA: older PyYAML


def materialize_config(raw: str) -> object:
    # Intentional CWE-502: unsafe_load is equivalent to the old default loader behavior
    return yaml.unsafe_load(raw)  # noqa: S506
