# RESEARCH: optional second process for folks who *really* need a small attack surface in a second terminal.
# Default Docker story is a single monolith; run this by hand: `python -m run_auth` (port 5001 by default).
import os

os.environ.setdefault("AUTH_SERVICE_MODE", "1")
os.environ.setdefault("SERVICE_NAME", "auth")
os.environ.setdefault("PORT", "5001")

from bookstore.app import create_app  # noqa: E402

if __name__ == "__main__":
    a = create_app()
    p = int(os.environ.get("PORT", "5001"))
    h = "0.0.0.0" if (os.environ.get("BIND_ALL", "1") or "1") == "1" else "127.0.0.1"
    a.run(host=h, port=p, debug=True)
