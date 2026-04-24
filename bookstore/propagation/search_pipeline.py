"""Search and filter text flows from HTTP params toward SQL string assembly (inventory list)."""
from __future__ import annotations

from typing import Any, Dict, List

from bookstore.sync.merge_state import tag_search


def build_list_clause(search: Dict[str, Any]) -> str:
    """Build SQL WHERE fragment — intentionally unsafe concatenation for demos."""
    parts: List[str] = []
    tagged = tag_search(
        {
            "q": search.get("q") or "",
            "author": search.get("author") or "",
        }
    )
    for key in ("q", "author"):
        val = tagged.get(key) or ""
        if not val:
            continue
        t = val.replace("'", "''")
        if key == "q":
            parts.append("title LIKE '%" + t + "%'")
        else:
            parts.append("author LIKE '%" + t + "%'")
    if not parts:
        return "1=1"
    return " AND ".join(parts)
