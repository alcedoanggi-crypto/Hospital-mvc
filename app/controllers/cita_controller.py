from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.cita import Cita, ESTADOS_CITA
from app.models.paciente import Paciente
from app.models.medico import Medico
from app.utils.decorators import role_required

citas_bp = Blueprint("citas", __name__, url_prefix="/citas")

GESTORES = ("administrador", "recepcionista", "medico")


def _parse_dt(valor):
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(valor, fmt)
        except (ValueError, TypeError):
            continue
    return None


@citas_bp.route("/")
@login_required
@role_required(*GESTORES)
def index():
    estado = request.args.get("estado", "")
    q = Cita.query
    if estado:
        q = q.filter(Cita.estado == estado)
    citas = q.order_by(Cita.fecha_hora.desc()).limit(200).all()
    return render_template("citas/index.html", citas=citas, estado=estado, estados=ESTADOS_CITA)


@citas_bp.route("/agenda")
@login_required
@role_required(*GESTORES)
def agenda():
    return render_template("citas/agenda.html")


@citas_bp.route("/<int:cid>")
@login_required
@role_required(*GESTORES)
def detalle(cid):
    cita = db.session.get(Cita, cid) or abort(404)
    return render_template("citas/detalle.html", cita=cita)


@citas_bp.route("/nueva", methods=["GET", "POST"])
@login_required
@role_required("administrador", "recepcionista", "medico")
def crear():
    pacientes = Paciente.query.order_by(Paciente.apellidos).all()
    medicos = Medico.query.filter_by(activo=True).order_by(Medico.apellidos).all()
    if request.method == "POST":
        c = Cita()
        _asignar(c, request.form)
        if not c.paciente_id or not c.medico_id or not c.fecha_hora:
            flash("Paciente, medico y fecha/hora son obligatorios.", "danger")
        else:
            db.session.add(c)
            db.session.commit()
            flash("Cita agendada.", "success")
            return redirect(url_for("citas.detalle", cid=c.id))
    return render_template(
        "citas/form.html", cita=Cita(), pacientes=pacientes, medicos=medicos, modo="crear",
        estados=ESTADOS_CITA,
    )


@citas_bp.route("/<int:cid>/editar", methods=["GET", "POST"])
@login_required
@role_required("administrador", "recepcionista", "medico")
def editar(cid):
    cita = db.session.get(Cita, cid) or abort(404)
    pacientes = Paciente.query.order_by(Paciente.apellidos).all()
    medicos = Medico.query.order_by(Medico.apellidos).all()
    if request.method == "POST":
        _asignar(cita, request.form)
        db.session.commit()
        flash("Cita actualizada.", "success")
        return redirect(url_for("citas.detalle", cid=cita.id))
    return render_template(
        "citas/form.html", cita=cita, pacientes=pacientes, medicos=medicos, modo="editar",
        estados=ESTADOS_CITA,
    )


@citas_bp.route("/<int:cid>/estado", methods=["POST"])
@login_required
@role_required(*GESTORES)
def cambiar_estado(cid):
    cita = db.session.get(Cita, cid) or abort(404)
    nuevo = request.form.get("estado")
    if nuevo in ESTADOS_CITA:
        cita.estado = nuevo
        db.session.commit()
        flash("Estado de la cita actualizado.", "success")
    return redirect(request.referrer or url_for("citas.detalle", cid=cid))


def _asignar(c, form):
    c.paciente_id = form.get("paciente_id", type=int)
    c.medico_id = form.get("medico_id", type=int)
    c.fecha_hora = _parse_dt(form.get("fecha_hora"))
    c.duracion_min = form.get("duracion_min", type=int) or 30
    c.motivo = form.get("motivo", "").strip() or None
    c.notas = form.get("notas", "").strip() or None
    estado = form.get("estado")
    if estado in ESTADOS_CITA:
        c.estado = estado
