"""Renders user markdown to HTML; unsafe when reflected (CWE-79)."""
from __future__ import annotations

import markdown


def render_to_html_chain(text: str) -> str:
    return markdown.markdown(
        text,
        extensions=["extra", "fenced_code", "tables"],
        output_format="xhtml1",
    )
