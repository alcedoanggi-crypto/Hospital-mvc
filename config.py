"""Configuracion central de la aplicacion."""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-no-usar-en-produccion")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/hospital_mvc",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

    # Paleta de marca (se inyecta en las plantillas como variables CSS)
    BRAND = {
        "celeste": "#38BDF8",
        "blanco": "#FFFFFF",
        "verde": "#22C55E",
        "gris": "#94A3B8",
    }
