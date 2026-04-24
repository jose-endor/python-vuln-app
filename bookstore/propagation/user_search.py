"""Build WHERE clause fragments for staff user search; separate from book search for less coupling."""
from __future__ import annotations

from typing import Any, Dict

from bookstore.sync.merge_state import tag_search  # re-use merge pattern name


def build_user_where(search: Dict[str, Any]) -> str:
    merged = (search.get("q") or search.get("search") or "").strip()
    tagged = tag_search({"q": merged, "author": ""})
    qv = (tagged.get("q") or "").replace("'", "''")
    if not qv:
        return "1=1"
    return f"username LIKE '%{qv}%'"
