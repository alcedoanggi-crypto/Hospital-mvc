from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required

from app.extensions import db
from app.models.historial import HistorialClinico
from app.models.paciente import Paciente
from app.models.medico import Medico
from app.models.cita import Cita
from app.utils.decorators import role_required

historiales_bp = Blueprint("historiales", __name__, url_prefix="/historiales")

CLINICOS = ("administrador", "medico")


@historiales_bp.route("/paciente/<int:pid>")
@login_required
@role_required("administrador", "medico", "recepcionista")
def por_paciente(pid):
    paciente = db.session.get(Paciente, pid) or abort(404)
    historiales = (
        HistorialClinico.query.filter_by(paciente_id=pid)
        .order_by(HistorialClinico.fecha.desc())
        .all()
    )
    return render_template(
        "historiales/paciente.html", paciente=paciente, historiales=historiales
    )


@historiales_bp.route("/<int:hid>")
@login_required
@role_required("administrador", "medico", "recepcionista")
def detalle(hid):
    h = db.session.get(HistorialClinico, hid) or abort(404)
    return render_template("historiales/detalle.html", h=h)


@historiales_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@role_required(*CLINICOS)
def crear():
    paciente_id = request.args.get("paciente_id", type=int)
    cita_id = request.args.get("cita_id", type=int)
    pacientes = Paciente.query.order_by(Paciente.apellidos).all()
    medicos = Medico.query.order_by(Medico.apellidos).all()

    if request.method == "POST":
        h = HistorialClinico()
        h.paciente_id = request.form.get("paciente_id", type=int)
        h.medico_id = request.form.get("medico_id", type=int)
        h.cita_id = request.form.get("cita_id", type=int) or None
        h.motivo_consulta = request.form.get("motivo_consulta", "").strip() or None
        h.diagnostico = request.form.get("diagnostico", "").strip()
        h.tratamiento = request.form.get("tratamiento", "").strip() or None
        h.observaciones = request.form.get("observaciones", "").strip() or None
        h.alergias = request.form.get("alergias", "").strip() or None

        if not h.paciente_id or not h.medico_id or not h.diagnostico:
            flash("Paciente, medico y diagnostico son obligatorios.", "danger")
        else:
            db.session.add(h)
            if h.cita_id:
                cita = db.session.get(Cita, h.cita_id)
                if cita and cita.estado == "programada":
                    cita.estado = "atendida"
            db.session.commit()
            flash("Historial clinico registrado.", "success")
            return redirect(url_for("historiales.detalle", hid=h.id))

    return render_template(
        "historiales/form.html",
        h=HistorialClinico(paciente_id=paciente_id, cita_id=cita_id),
        pacientes=pacientes,
        medicos=medicos,
    )
