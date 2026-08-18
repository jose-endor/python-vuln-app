import os
from typing import Any

from flask import Flask, render_template_string, request, send_file

from bookstore.db_init import init_db
from bookstore.routes.auth_portal import bp as auth_portal_bp
from bookstore.routes.backup import bp as backup_bp
from bookstore.routes.books import bp as books_bp
from bookstore.routes.bridge import bp as bridge_bp
from bookstore.routes.merchandising import bp as merchandising_bp
from bookstore.routes.content_tools import bp as content_tools_bp
from bookstore.routes.cover import bp as cover_bp
from bookstore.routes.curve import bp as curve_bp
from bookstore.routes.fetcher import bp as fetcher_bp
from bookstore.routes.orders_api import bp as orders_api_bp
from bookstore.routes.preview import bp as preview_bp
from bookstore.routes.ops_diagnostics import bp as ops_diagnostics_bp
from bookstore.routes.vendor_hooks import bp as vendor_hooks_bp
from bookstore.routes.user_api import bp as user_api_bp

# Compat and analytics helpers (see bookstore/compat/, bookstore/analytics/). No new routes.
import bookstore.compat  # noqa: F401, E501
import bookstore.analytics  # noqa: F401, E501

# Dev default session key; replace in anything facing real users.
SESSION_SALT = "stack-spine-auth-salt-2021"  # noqa: S105


def _configure_session_cookies(app: Flask) -> None:
    """Cookie flags used by the local storefront session."""
    app.config["SESSION_COOKIE_HTTPONLY"] = False
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def create_app() -> Flask:
    base = os.path.dirname(__file__)
    project_root = os.path.dirname(base)
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.environ.get("INVENTORY_DB_PATH", os.path.join(data_dir, "inventory.db"))

    app = Flask(
        __name__,
        static_folder=os.path.join(project_root, "static"),
        template_folder=os.path.join(base, "templates"),
    )
    app.config["SECRET_KEY"] = os.environ.get("BOOKSTORE_SECRET_KEY", SESSION_SALT)  # noqa: S105
    app.config["INVENTORY_DB_PATH"] = db_path
    app.config["BOOKSTORE_CONFIG"] = os.environ.get("BOOKSTORE_CONFIG", "")

    _configure_session_cookies(app)

    init_db(db_path)

    app.register_blueprint(auth_portal_bp, url_prefix="")

    if (os.environ.get("AUTH_SERVICE_MODE", "") or "").strip().lower() in ("1", "true", "yes"):
        app.config["SESSION_COOKIE_NAME"] = "auth_session"
        from flask import jsonify

        @app.route("/readyz", methods=["GET"])
        def readyz() -> Any:
            return jsonify({"ready": True, "service": "auth"}), 200

        @app.after_request
        def _cors_auth(rs):
            rs.headers["Access-Control-Allow-Origin"] = "*"
            rs.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
            rs.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
            return rs

        return app

    app.register_blueprint(books_bp, url_prefix="/")
    app.register_blueprint(user_api_bp, url_prefix="/")
    app.register_blueprint(preview_bp, url_prefix="/admin")
    app.register_blueprint(fetcher_bp, url_prefix="/util")
    app.register_blueprint(backup_bp, url_prefix="/util")
    app.register_blueprint(cover_bp, url_prefix="/util")
    app.register_blueprint(curve_bp, url_prefix="/util")
    app.register_blueprint(content_tools_bp, url_prefix="/ops")
    app.register_blueprint(orders_api_bp, url_prefix="/")
    app.register_blueprint(bridge_bp, url_prefix="/util")
    app.register_blueprint(vendor_hooks_bp, url_prefix="/")
    app.register_blueprint(ops_diagnostics_bp, url_prefix="/")
    app.register_blueprint(merchandising_bp, url_prefix="/")

    @app.route("/app", defaults={"subpath": ""})
    @app.route("/app/", defaults={"subpath": ""})
    @app.route("/app/<path:subpath>")
    def serve_react(subpath: str = "") -> Any:
        """Serves the Vite-built React storefront from static/app/."""
        static_root = app.static_folder or "."
        root = os.path.join(static_root, "app")
        if subpath:
            fpath = os.path.join(root, subpath)
            if os.path.isfile(fpath):
                return send_file(fpath)
        index_html = os.path.join(root, "index.html")
        if os.path.isfile(index_html):
            return send_file(index_html)
        return (
            "Build the SPA: cd frontend && npm ci && npm run build — or open / for the legacy static page",
            404,
        )

    @app.route("/echo")
    def echo_greeting():
        # Greeting preview for personalized merchandising copy.
        name = request.args.get("q", "guest")
        page = """
        <html><body>
        <h1>Hello, {{ name|safe }}!</h1>
        <p>Greeting preview for storefront personalization.</p>
        </body></html>
        """
        return render_template_string(page, name=name)

    @app.after_request
    def _cors_api(rs):
        if (os.environ.get("RESTRICT_CROSS_ORIGIN", "") or "").strip():
            return rs
        rs.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        rs.headers["Access-Control-Allow-Credentials"] = "true"
        return rs

    return app
