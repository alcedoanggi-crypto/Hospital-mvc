"""Fabrica de la aplicacion Flask (patron MVC).

- models/       -> Modelos (capa de datos, SQLAlchemy + PostgreSQL)
- controllers/  -> Controladores (blueprints con la logica de rutas)
- templates/    -> Vistas (HTML + Bootstrap 5)
"""
from flask import Flask, render_template

from config import Config
from app.extensions import db, migrate, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Extensiones ---
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Importa modelos para que Flask-Migrate los registre
    from app import models  # noqa: F401

    # --- Controladores (blueprints) ---
    from app.controllers.auth_controller import auth_bp
    from app.controllers.dashboard_controller import dashboard_bp
    from app.controllers.paciente_controller import pacientes_bp
    from app.controllers.medico_controller import medicos_bp
    from app.controllers.especialidad_controller import especialidades_bp
    from app.controllers.cita_controller import citas_bp
    from app.controllers.historial_controller import historiales_bp
    from app.controllers.receta_controller import recetas_bp
    from app.controllers.examen_controller import examenes_bp
    from app.controllers.factura_controller import facturas_bp
    from app.controllers.api_controller import api_bp

    for bp in (
        auth_bp,
        dashboard_bp,
        pacientes_bp,
        medicos_bp,
        especialidades_bp,
        citas_bp,
        historiales_bp,
        recetas_bp,
        examenes_bp,
        facturas_bp,
        api_bp,
    ):
        app.register_blueprint(bp)

    # --- Contexto de plantillas: paleta de marca ---
    @app.context_processor
    def inject_brand():
        return {"BRAND": app.config["BRAND"]}

    # --- Manejo de errores ---
    @app.errorhandler(403)
    def forbidden(_):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_):
        return render_template("errors/404.html"), 404

    @app.errorhandler(401)
    def unauthorized(_):
        return render_template("errors/403.html"), 401

    # --- Comandos CLI ---
    from app.cli import register_cli

    register_cli(app)

    return app
