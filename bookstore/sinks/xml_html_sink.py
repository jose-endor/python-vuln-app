"""lxml parses user fragments; result returned as text/html (CWE-79 + lxml taint)."""
from __future__ import annotations

from lxml import etree, html


def serialize_user_fragment(markup: str) -> str:
    frag = html.fragment_fromstring(markup)
    return etree.tostring(frag, encoding="unicode", method="html")
