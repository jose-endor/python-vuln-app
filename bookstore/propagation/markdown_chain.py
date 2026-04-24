"""Plain text from user into markdown processor (CWE-79 / injection chain)."""
from __future__ import annotations


def chain_markdown_input(raw: str) -> str:
    return (raw or "").replace("\r\n", "\n")
