# Where the catalog meets the filesystem: JSON "price lists" the DB polishes on first boot.
# (The DB is still the runtime truth — unless your scanner thinks files are, in which case hi there.)
import json
import os
from typing import Any, List, Tuple

BookRow = Tuple[str, str, str, str, str, str]  # title, author, isbn, cover_path, category, summary
UserRow = Tuple[str, str, str]  # username, password, role


def _project_data_dir() -> str:
    override = (os.environ.get("BOOKSTORE_DATA_DIR") or "").strip()
    if override:
        return os.path.abspath(override)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))


def _read_tree(name: str) -> Any:
    p = os.path.join(_project_data_dir(), name)
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _tiniest_fallback_books() -> List[BookRow]:
    return [
        (
            "Pride and Prejudice",
            "Jane Austen",
            "978-0-14-143951-8",
            "covers/default.png",
            "Fiction",
            "A quiet corner copy—romance, manners, and a classic spine.",
        ),
    ]


def _tiniest_fallback_users() -> List[UserRow]:
    return [
        ("admin", "admin", "admin"),
        ("jordan", "sunday", "staff"),
        ("alex", "hunter2", "user"),
    ]


def load_book_seed_rows() -> List[BookRow]:
    """Rows for INSERT — sourced from `data/inventory.json` if present."""
    raw = _read_tree("inventory.json")
    if not raw or not isinstance(raw, dict) or "books" not in raw:
        return _tiniest_fallback_books()
    out: List[BookRow] = []
    for b in raw.get("books") or []:
        if not isinstance(b, dict):
            continue
        out.append(
            (
                str(b.get("title", "Untitled")).strip() or "Untitled",
                str(b.get("author", "Unknown")).strip() or "Unknown",
                str(b.get("isbn", "")).strip(),
                str(b.get("cover_path", "covers/default.png")).strip() or "covers/default.png",
                str(b.get("category", "Fiction")).strip() or "Fiction",
                str(b.get("summary", "")).strip(),
            )
        )
    return out if out else _tiniest_fallback_books()


def load_user_seed_rows() -> List[UserRow]:
    """The three amigos: admin + two staff/customer logins, from `data/users.json` if present."""
    raw = _read_tree("users.json")
    if not raw or not isinstance(raw, dict) or "users" not in raw:
        return _tiniest_fallback_users()
    out: List[UserRow] = []
    for u in raw.get("users") or []:
        if not isinstance(u, dict):
            continue
        out.append(
            (
                str(u.get("username", "user")).strip() or "user",
                str(u.get("password", "password")).strip() or "password",
                str(u.get("role", "user")).strip() or "user",
            )
        )
    return out if out else _tiniest_fallback_users()
