import os

from flask import Flask, render_template_string, request

from bookstore.db_init import init_db
from bookstore.routes.books import bp as books_bp
from bookstore.routes.preview import bp as preview_bp
from bookstore.routes.fetcher import bp as fetcher_bp
from bookstore.routes.backup import bp as backup_bp
from bookstore.routes.cover import bp as cover_bp
from bookstore.routes.curve import bp as curve_bp
from bookstore.routes.lab import bp as lab_bp
from bookstore.routes.bridge import bp as bridge_bp
from bookstore.routes.sca_demos import bp as sca_bp
from bookstore.routes.sast_stress import bp as sast_stress_bp


# Hardcoded "secret" for secret-scanner / misconfig storylines
DEV_SESSION_SALT = "dev-salt-CHANGE-ME-RESEARCH-ONLY"  # noqa: S105


def create_app():
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

    init_db(db_path)

    app.register_blueprint(books_bp, url_prefix="/")
    app.register_blueprint(preview_bp, url_prefix="/admin")
    app.register_blueprint(fetcher_bp, url_prefix="/util")
    app.register_blueprint(backup_bp, url_prefix="/util")
    app.register_blueprint(cover_bp, url_prefix="/util")
    app.register_blueprint(curve_bp, url_prefix="/util")
    app.register_blueprint(lab_bp, url_prefix="/lab")
    app.register_blueprint(bridge_bp, url_prefix="/util")
    app.register_blueprint(sca_bp, url_prefix="/")
    app.register_blueprint(sast_stress_bp, url_prefix="/")

    @app.route("/echo")
    def echo_xss():
        # Source at route — reflected in template string (SAST: XSS)
        name = request.args.get("q", "guest")
        page = """
        <html><body>
        <h1>Hello, {{ name|safe }}!</h1>
        <p>Try <code>/echo?q=&lt;script&gt;...&lt;/script&gt;</code> (demo only)</p>
        </body></html>
        """
        return render_template_string(page, name=name)

    return app
