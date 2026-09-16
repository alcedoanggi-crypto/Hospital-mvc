from datetime import datetime

from app.extensions import db


class HistorialClinico(db.Model):
    __tablename__ = "historiales_clinicos"

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey("medicos.id"), nullable=False)
    cita_id = db.Column(db.Integer, db.ForeignKey("citas.id"))

    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    motivo_consulta = db.Column(db.String(255))
    diagnostico = db.Column(db.Text, nullable=False)
    tratamiento = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    alergias = db.Column(db.Text)

    paciente = db.relationship("Paciente", back_populates="historiales")
    medico = db.relationship("Medico")
    cita = db.relationship("Cita", back_populates="historial")
    recetas = db.relationship("Receta", back_populates="historial")

    def __repr__(self):
        return f"<HistorialClinico {self.id} paciente={self.paciente_id}>"
