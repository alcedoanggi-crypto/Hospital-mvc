from datetime import datetime
from decimal import Decimal

from app.extensions import db

ESTADOS_FACTURA = ("pendiente", "pagada", "anulada")
IGV = Decimal("0.18")


class Factura(db.Model):
    __tablename__ = "facturas"

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False)
    cita_id = db.Column(db.Integer, db.ForeignKey("citas.id"))

    numero = db.Column(db.String(20), unique=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    impuesto = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    metodo_pago = db.Column(db.String(30))
    # [{"concepto": "...", "cantidad": 1, "precio": 0.0}]
    detalle = db.Column(db.JSON, nullable=False, default=list)

    paciente = db.relationship("Paciente", back_populates="facturas")
    cita = db.relationship("Cita", back_populates="factura")

    def recalcular(self):
        sub = Decimal("0")
        for item in self.detalle or []:
            sub += Decimal(str(item.get("precio", 0))) * int(item.get("cantidad", 1))
        self.subtotal = sub
        self.impuesto = (sub * IGV).quantize(Decimal("0.01"))
        self.total = self.subtotal + self.impuesto

    def __repr__(self):
        return f"<Factura {self.numero or self.id} {self.estado}>"
