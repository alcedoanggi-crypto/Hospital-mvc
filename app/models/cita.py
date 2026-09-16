from datetime import datetime

from app.extensions import db

ESTADOS_CITA = ("programada", "atendida", "cancelada", "no_asistio")


class Cita(db.Model):
    __tablename__ = "citas"

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey("medicos.id"), nullable=False)

    fecha_hora = db.Column(db.DateTime, nullable=False, index=True)
    duracion_min = db.Column(db.Integer, nullable=False, default=30)
    motivo = db.Column(db.String(255))
    estado = db.Column(db.String(20), nullable=False, default="programada")
    notas = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    paciente = db.relationship("Paciente", back_populates="citas")
    medico = db.relationship("Medico", back_populates="citas")
    historial = db.relationship("HistorialClinico", back_populates="cita", uselist=False)
    factura = db.relationship("Factura", back_populates="cita", uselist=False)

    def __repr__(self):
        return f"<Cita {self.id} {self.fecha_hora:%Y-%m-%d %H:%M} {self.estado}>"
