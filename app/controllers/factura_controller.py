from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required

from app.extensions import db
from app.models.factura import Factura, ESTADOS_FACTURA
from app.models.paciente import Paciente
from app.models.cita import Cita
from app.utils.decorators import role_required

facturas_bp = Blueprint("facturas", __name__, url_prefix="/facturas")

FACTURACION = ("administrador", "recepcionista")


@facturas_bp.route("/")
@login_required
@role_required(*FACTURACION)
def index():
    estado = request.args.get("estado", "")
    q = Factura.query
    if estado:
        q = q.filter(Factura.estado == estado)
    facturas = q.order_by(Factura.fecha.desc()).limit(200).all()
    total_pendiente = sum(float(f.total) for f in Factura.query.filter_by(estado="pendiente"))
    return render_template(
        "facturas/index.html", facturas=facturas, estado=estado,
        estados=ESTADOS_FACTURA, total_pendiente=total_pendiente,
    )


@facturas_bp.route("/<int:fid>")
@login_required
@role_required(*FACTURACION)
def detalle(fid):
    f = db.session.get(Factura, fid) or abort(404)
    return render_template("facturas/detalle.html", f=f)


@facturas_bp.route("/nueva", methods=["GET", "POST"])
@login_required
@role_required(*FACTURACION)
def crear():
    pacientes = Paciente.query.order_by(Paciente.apellidos).all()
    citas = Cita.query.filter(Cita.estado == "atendida").order_by(Cita.fecha_hora.desc()).limit(100).all()
    if request.method == "POST":
        f = Factura()
        f.paciente_id = request.form.get("paciente_id", type=int)
        f.cita_id = request.form.get("cita_id", type=int) or None
        f.metodo_pago = request.form.get("metodo_pago", "").strip() or None
        f.estado = request.form.get("estado") if request.form.get("estado") in ESTADOS_FACTURA else "pendiente"

        detalle = []
        conceptos = request.form.getlist("concepto")
        cantidades = request.form.getlist("cantidad")
        precios = request.form.getlist("precio")
        for i, con in enumerate(conceptos):
            if con.strip():
                detalle.append({
                    "concepto": con.strip(),
                    "cantidad": int(cantidades[i] or 1) if i < len(cantidades) else 1,
                    "precio": float(precios[i] or 0) if i < len(precios) else 0.0,
                })
        f.detalle = detalle
        f.recalcular()

        if not f.paciente_id or not detalle:
            flash("Paciente y al menos un concepto son obligatorios.", "danger")
        else:
            db.session.add(f)
            db.session.flush()
            f.numero = f"F-{f.id:05d}"
            db.session.commit()
            flash("Factura generada.", "success")
            return redirect(url_for("facturas.detalle", fid=f.id))
    return render_template("facturas/form.html", pacientes=pacientes, citas=citas, estados=ESTADOS_FACTURA)


@facturas_bp.route("/<int:fid>/pagar", methods=["POST"])
@login_required
@role_required(*FACTURACION)
def pagar(fid):
    f = db.session.get(Factura, fid) or abort(404)
    f.estado = "pagada"
    f.metodo_pago = request.form.get("metodo_pago", f.metodo_pago)
    db.session.commit()
    flash("Factura marcada como pagada.", "success")
    return redirect(url_for("facturas.detalle", fid=fid))
