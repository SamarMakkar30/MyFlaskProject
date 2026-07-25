import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL


# Loading here keeps `flask db ...`, `seed.py`, and `python app.py` consistent.
# Environment variables always take precedence over values in a local .env file.
load_dotenv()


def _env_port(name, default):
    """Return a valid port number without making an invalid .env fatal at import time."""
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


class Config:
    """Application configuration sourced from the environment, never from secrets in code."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-local-development-key")

    # These local defaults make first-run setup straightforward. DB_PASSWORD deliberately
    # has no source-code value: set it in .env (or in the host environment) when needed.
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = _env_port("DB_PORT", 3306)
    DB_NAME = os.environ.get("DB_NAME", "employee_db")

    # URL.create safely escapes special characters in usernames and passwords.
    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        query={"charset": "utf8mb4"},
    ).render_as_string(hide_password=False)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    APP_NAME = "Employee Management System"
    UPLOAD_FOLDER = "uploads"
    DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() in {"1", "true", "yes", "on"}
