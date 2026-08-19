# Optional auth service process for local multi-service setups.
# Default Docker compose runs a single monolith; start this separately with:
#   python -m run_auth
# (listens on port 5001 by default).
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
