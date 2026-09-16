from datetime import datetime

from app.extensions import db

ESTADOS_EXAMEN = ("solicitado", "en_proceso", "completado", "anulado")


class Examen(db.Model):
    __tablename__ = "examenes"

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey("medicos.id"), nullable=False)
    cita_id = db.Column(db.Integer, db.ForeignKey("citas.id"))

    tipo = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text)
    resultado = db.Column(db.Text)
    estado = db.Column(db.String(20), nullable=False, default="solicitado")
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_resultado = db.Column(db.DateTime)

    paciente = db.relationship("Paciente", back_populates="examenes")
    medico = db.relationship("Medico")

    def __repr__(self):
        return f"<Examen {self.id} {self.tipo} {self.estado}>"
