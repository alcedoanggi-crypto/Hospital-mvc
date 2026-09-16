from datetime import datetime

from app.extensions import db


class Receta(db.Model):
    __tablename__ = "recetas"

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey("medicos.id"), nullable=False)
    historial_id = db.Column(db.Integer, db.ForeignKey("historiales_clinicos.id"))

    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    diagnostico = db.Column(db.String(255))
    indicaciones = db.Column(db.Text)
    # Lista de medicamentos en formato JSON:
    # [{"medicamento": "...", "dosis": "...", "frecuencia": "...", "duracion": "..."}]
    medicamentos = db.Column(db.JSON, nullable=False, default=list)

    paciente = db.relationship("Paciente", back_populates="recetas")
    medico = db.relationship("Medico")
    historial = db.relationship("HistorialClinico", back_populates="recetas")

    def __repr__(self):
        return f"<Receta {self.id} paciente={self.paciente_id}>"
