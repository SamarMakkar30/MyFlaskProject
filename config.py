import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL
load_dotenv()
def _env_port(name, default):
    try: return int(os.environ.get(name, default))
    except (TypeError, ValueError): return default
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-local-development-key")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = _env_port("DB_PORT", 3306)
    DB_NAME = os.environ.get("DB_NAME", "employee_db")
    SQLALCHEMY_DATABASE_URI = URL.create(drivername="mysql+pymysql", username=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME, query={"charset":"utf8mb4"}).render_as_string(hide_password=False)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}
    APP_NAME = "OrbitHR"
    UPLOAD_FOLDER = "uploads"
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() in {"1","true","yes","on"}
