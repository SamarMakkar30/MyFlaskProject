from flask import Flask, render_template
from flask_migrate import Migrate
from sqlalchemy.exc import DBAPIError, OperationalError

from config import Config
from app.models import db
from app.routes.department import department_bp
from app.routes.employee import employee_bp
from app.routes.home import home_bp


migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(home_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(department_bp)

    @app.errorhandler(OperationalError)
    @app.errorhandler(DBAPIError)
    def handle_database_unavailable(error):
        """Keep transient MySQL outages from exposing a driver traceback to users."""
        try:
            db.session.rollback()
        except Exception:
            # A failed connection may not have created a transaction to roll back.
            pass

        app.logger.warning("Database request failed: %s", error)
        return render_template("database_unavailable.html"), 503

    return app
