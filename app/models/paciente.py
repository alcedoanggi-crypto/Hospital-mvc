from datetime import datetime

from app.extensions import db


class Paciente(db.Model):
    __tablename__ = "pacientes"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), unique=True)

    nombres = db.Column(db.String(120), nullable=False)
    apellidos = db.Column(db.String(120), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False, index=True)
    fecha_nacimiento = db.Column(db.Date)
    sexo = db.Column(db.String(1))  # M / F / O
    telefono = db.Column(db.String(30))
    direccion = db.Column(db.String(200))
    email = db.Column(db.String(160))
    tipo_sangre = db.Column(db.String(4))
    alergias = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("Usuario", back_populates="paciente")
    citas = db.relationship("Cita", back_populates="paciente")
    historiales = db.relationship("HistorialClinico", back_populates="paciente")
    recetas = db.relationship("Receta", back_populates="paciente")
    examenes = db.relationship("Examen", back_populates="paciente")
    facturas = db.relationship("Factura", back_populates="paciente")

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    def __repr__(self):
        return f"<Paciente {self.dni} {self.nombre_completo}>"
