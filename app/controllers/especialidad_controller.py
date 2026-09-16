from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required

from app.extensions import db
from app.models.especialidad import Especialidad
from app.utils.decorators import role_required

especialidades_bp = Blueprint("especialidades", __name__, url_prefix="/especialidades")


@especialidades_bp.route("/")
@login_required
@role_required("administrador", "recepcionista")
def index():
    especialidades = Especialidad.query.order_by(Especialidad.nombre).all()
    return render_template("especialidades/index.html", especialidades=especialidades)


@especialidades_bp.route("/nueva", methods=["GET", "POST"])
@especialidades_bp.route("/<int:eid>/editar", methods=["GET", "POST"])
@login_required
@role_required("administrador")
def guardar(eid=None):
    esp = db.session.get(Especialidad, eid) if eid else Especialidad()
    if eid and esp is None:
        abort(404)
    if request.method == "POST":
        esp.nombre = request.form.get("nombre", "").strip()
        esp.descripcion = request.form.get("descripcion", "").strip() or None
        try:
            esp.precio_consulta = Decimal(request.form.get("precio_consulta") or "0")
        except InvalidOperation:
            esp.precio_consulta = Decimal("0")
        if not esp.nombre:
            flash("El nombre es obligatorio.", "danger")
        else:
            if not eid:
                db.session.add(esp)
            db.session.commit()
            flash("Especialidad guardada.", "success")
            return redirect(url_for("especialidades.index"))
    return render_template("especialidades/form.html", esp=esp, modo="editar" if eid else "crear")
