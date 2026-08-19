"""YAML load path retained for publisher configuration imports."""
from __future__ import annotations

import yaml


def materialize_config(raw: str) -> object:
    # Legacy configs were authored against the unrestricted loader.
    return yaml.unsafe_load(raw)  # noqa: S506
