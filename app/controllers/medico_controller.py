from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required

from app.extensions import db
from app.models.medico import Medico
from app.models.especialidad import Especialidad
from app.utils.decorators import role_required

medicos_bp = Blueprint("medicos", __name__, url_prefix="/medicos")


@medicos_bp.route("/")
@login_required
@role_required("administrador", "recepcionista", "medico")
def index():
    medicos = Medico.query.order_by(Medico.apellidos.asc()).all()
    return render_template("medicos/index.html", medicos=medicos)


@medicos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@role_required("administrador")
def crear():
    especialidades = Especialidad.query.order_by(Especialidad.nombre).all()
    if request.method == "POST":
        m = Medico()
        _asignar(m, request.form)
        if not m.nombres or not m.apellidos or not m.colegiatura or not m.especialidad_id:
            flash("Completa nombres, apellidos, colegiatura y especialidad.", "danger")
            return render_template("medicos/form.html", medico=m, especialidades=especialidades, modo="crear")
        db.session.add(m)
        db.session.commit()
        flash("Medico registrado.", "success")
        return redirect(url_for("medicos.index"))
    return render_template("medicos/form.html", medico=Medico(), especialidades=especialidades, modo="crear")


@medicos_bp.route("/<int:mid>/editar", methods=["GET", "POST"])
@login_required
@role_required("administrador")
def editar(mid):
    medico = db.session.get(Medico, mid) or abort(404)
    especialidades = Especialidad.query.order_by(Especialidad.nombre).all()
    if request.method == "POST":
        _asignar(medico, request.form)
        db.session.commit()
        flash("Medico actualizado.", "success")
        return redirect(url_for("medicos.index"))
    return render_template("medicos/form.html", medico=medico, especialidades=especialidades, modo="editar")


def _asignar(m, form):
    m.nombres = form.get("nombres", "").strip()
    m.apellidos = form.get("apellidos", "").strip()
    m.colegiatura = form.get("colegiatura", "").strip()
    m.telefono = form.get("telefono", "").strip() or None
    m.especialidad_id = form.get("especialidad_id", type=int)
    m.activo = bool(form.get("activo"))
