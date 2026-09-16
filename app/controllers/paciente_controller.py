from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required
from sqlalchemy import or_

from app.extensions import db
from app.models.paciente import Paciente
from app.utils.decorators import role_required

pacientes_bp = Blueprint("pacientes", __name__, url_prefix="/pacientes")

GESTORES = ("administrador", "recepcionista", "medico")


def _parse_fecha(valor):
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError:
        return None


@pacientes_bp.route("/")
@login_required
@role_required(*GESTORES)
def index():
    q = request.args.get("q", "").strip()
    sexo = request.args.get("sexo", "").strip()
    page = request.args.get("page", 1, type=int)

    consulta = Paciente.query
    if q:
        like = f"%{q}%"
        consulta = consulta.filter(
            or_(
                Paciente.nombres.ilike(like),
                Paciente.apellidos.ilike(like),
                Paciente.dni.ilike(like),
                Paciente.email.ilike(like),
            )
        )
    if sexo:
        consulta = consulta.filter(Paciente.sexo == sexo)

    pacientes = consulta.order_by(Paciente.apellidos.asc()).paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template("pacientes/index.html", pacientes=pacientes, q=q, sexo=sexo)


@pacientes_bp.route("/<int:pid>")
@login_required
@role_required(*GESTORES)
def detalle(pid):
    paciente = db.session.get(Paciente, pid) or abort(404)
    return render_template("pacientes/detalle.html", paciente=paciente)


@pacientes_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@role_required("administrador", "recepcionista")
def crear():
    if request.method == "POST":
        p = Paciente()
        _asignar(p, request.form)
        if not p.nombres or not p.apellidos or not p.dni:
            flash("Nombres, apellidos y DNI son obligatorios.", "danger")
            return render_template("pacientes/form.html", paciente=p, modo="crear")
        if Paciente.query.filter_by(dni=p.dni).first():
            flash("Ya existe un paciente con ese DNI.", "danger")
            return render_template("pacientes/form.html", paciente=p, modo="crear")
        db.session.add(p)
        db.session.commit()
        flash("Paciente registrado.", "success")
        return redirect(url_for("pacientes.detalle", pid=p.id))
    return render_template("pacientes/form.html", paciente=Paciente(), modo="crear")


@pacientes_bp.route("/<int:pid>/editar", methods=["GET", "POST"])
@login_required
@role_required("administrador", "recepcionista")
def editar(pid):
    paciente = db.session.get(Paciente, pid) or abort(404)
    if request.method == "POST":
        _asignar(paciente, request.form)
        db.session.commit()
        flash("Datos actualizados.", "success")
        return redirect(url_for("pacientes.detalle", pid=paciente.id))
    return render_template("pacientes/form.html", paciente=paciente, modo="editar")


@pacientes_bp.route("/<int:pid>/eliminar", methods=["POST"])
@login_required
@role_required("administrador")
def eliminar(pid):
    paciente = db.session.get(Paciente, pid) or abort(404)
    db.session.delete(paciente)
    db.session.commit()
    flash("Paciente eliminado.", "info")
    return redirect(url_for("pacientes.index"))


def _asignar(p, form):
    p.nombres = form.get("nombres", "").strip()
    p.apellidos = form.get("apellidos", "").strip()
    p.dni = form.get("dni", "").strip()
    p.fecha_nacimiento = _parse_fecha(form.get("fecha_nacimiento"))
    p.sexo = form.get("sexo") or None
    p.telefono = form.get("telefono", "").strip() or None
    p.direccion = form.get("direccion", "").strip() or None
    p.email = form.get("email", "").strip() or None
    p.tipo_sangre = form.get("tipo_sangre", "").strip() or None
    p.alergias = form.get("alergias", "").strip() or None
