import secrets
from flask import Flask, abort, redirect, render_template, request, session, url_for
from flask_migrate import Migrate
from sqlalchemy.exc import DBAPIError, OperationalError
from config import Config
from app.models import db
from app.routes.department import department_bp
from app.routes.employee import employee_bp
from app.routes.home import home_bp
from app.routes.auth import auth_bp

migrate = Migrate()

def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or Config)
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(home_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(auth_bp)

    @app.context_processor
    def csrf_context():
        token = session.setdefault("csrf_token", secrets.token_urlsafe(32))
        return {"csrf_token": token}

    @app.before_request
    def protect_state_changes():
        public = {"auth.login", "static"}
        if request.endpoint not in public and not session.get("user_id"):
            if request.path.startswith("/static/"):
                return None
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return {"error": "Authentication required"}, 401
            return redirect(url_for("auth.login", next=request.url))
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            supplied = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")
            if not supplied or not secrets.compare_digest(session.get("csrf_token", ""), supplied):
                abort(400, description="Your form session expired. Please try again.")

    @app.errorhandler(OperationalError)
    @app.errorhandler(DBAPIError)
    def handle_database_unavailable(error):
        try:
            db.session.rollback()
        except Exception:
            pass
        app.logger.warning("Database request failed: %s", error)
        return render_template("database_unavailable.html"), 503

    return app
