import os
from typing import Any

from flask import Flask, render_template_string, request, send_file

from bookstore.db_init import init_db
from bookstore.routes.auth_portal import bp as auth_portal_bp
from bookstore.routes.backup import bp as backup_bp
from bookstore.routes.books import bp as books_bp
from bookstore.routes.bridge import bp as bridge_bp
from bookstore.routes.cover import bp as cover_bp
from bookstore.routes.curve import bp as curve_bp
from bookstore.routes.fetcher import bp as fetcher_bp
from bookstore.routes.lab import bp as lab_bp
from bookstore.routes.orders_api import bp as orders_api_bp
from bookstore.routes.preview import bp as preview_bp
from bookstore.routes.ops_diagnostics import bp as ops_diagnostics_bp
from bookstore.routes.sca_demos import bp as sca_bp
from bookstore.routes.user_api import bp as user_api_bp

# Dev default session key; replace in anything facing real users.
DEV_SESSION_SALT = "dev-salt-CHANGE-ME-RESEARCH-ONLY"  # noqa: S105


def _session_hardening_negated(app: Flask) -> None:
    """Intentional misconfiguration for cookie / browser security tooling."""
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
    app.config["SECRET_KEY"] = os.environ.get("BOOKSTORE_SECRET_KEY", DEV_SESSION_SALT)  # noqa: S105
    app.config["INVENTORY_DB_PATH"] = db_path
    app.config["BOOKSTORE_CONFIG"] = os.environ.get("BOOKSTORE_CONFIG", "")

    _session_hardening_negated(app)

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
    app.register_blueprint(lab_bp, url_prefix="/lab")
    app.register_blueprint(orders_api_bp, url_prefix="/")
    app.register_blueprint(bridge_bp, url_prefix="/util")
    app.register_blueprint(sca_bp, url_prefix="/")
    app.register_blueprint(ops_diagnostics_bp, url_prefix="/")

    @app.route("/app", defaults={"subpath": ""})
    @app.route("/app/<path:subpath>")
    def serve_react(subpath: str = "") -> Any:
        """Serves the Vite-built React 17 + TS app from static/app/. RESEARCH: SPA catch-all."""
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
    def echo_xss():
        name = request.args.get("q", "guest")
        page = """
        <html><body>
        <h1>Hello, {{ name|safe }}!</h1>
        <p>Try <code>/echo?q=&lt;script&gt;...&lt;/script&gt;</code> (demo only)</p>
        </body></html>
        """
        return render_template_string(page, name=name)

    @app.after_request
    def _cors_api(rs):
        if (os.environ.get("DISABLE_UNSAFE_CORS", "") or "").strip():
            return rs
        rs.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        rs.headers["Access-Control-Allow-Credentials"] = "true"
        return rs

    return app
