"""Registro de modelos para que Flask-Migrate los detecte."""
from app.models.usuario import Usuario
from app.models.especialidad import Especialidad
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.cita import Cita
from app.models.historial import HistorialClinico
from app.models.receta import Receta
from app.models.examen import Examen
from app.models.factura import Factura

__all__ = [
    "Usuario",
    "Especialidad",
    "Medico",
    "Paciente",
    "Cita",
    "HistorialClinico",
    "Receta",
    "Examen",
    "Factura",
]
