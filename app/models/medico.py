from app.extensions import db


class Medico(db.Model):
    __tablename__ = "medicos"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), unique=True)
    especialidad_id = db.Column(
        db.Integer, db.ForeignKey("especialidades.id"), nullable=False
    )

    nombres = db.Column(db.String(120), nullable=False)
    apellidos = db.Column(db.String(120), nullable=False)
    colegiatura = db.Column(db.String(40), unique=True, nullable=False)
    telefono = db.Column(db.String(30))
    activo = db.Column(db.Boolean, nullable=False, default=True)

    usuario = db.relationship("Usuario", back_populates="medico")
    especialidad = db.relationship("Especialidad", back_populates="medicos")
    citas = db.relationship("Cita", back_populates="medico")

    @property
    def nombre_completo(self):
        return f"Dr(a). {self.nombres} {self.apellidos}"

    def __repr__(self):
        return f"<Medico {self.nombre_completo}>"
