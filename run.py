import os

from bookstore.app import create_app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", "3333"))
    # Local use: http://127.0.0.1:3333/ — not for production
    app.run(host="127.0.0.1", port=port, debug=True)
