import os

from bookstore.app import create_app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", "3333"))
    h = "0.0.0.0" if (os.environ.get("BIND_ALL", "0") or "0") == "1" else "127.0.0.1"
    # Local: http://127.0.0.1:3333/ — in Docker: set BIND_ALL=1
    app.run(host=h, port=port, debug=True)
