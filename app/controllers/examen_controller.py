from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required

from app.extensions import db
from app.models.examen import Examen, ESTADOS_EXAMEN
from app.models.paciente import Paciente
from app.models.medico import Medico
from app.utils.decorators import role_required

examenes_bp = Blueprint("examenes", __name__, url_prefix="/examenes")

GESTORES = ("administrador", "medico", "recepcionista")


@examenes_bp.route("/")
@login_required
@role_required(*GESTORES)
def index():
    estado = request.args.get("estado", "")
    q = Examen.query
    if estado:
        q = q.filter(Examen.estado == estado)
    examenes = q.order_by(Examen.fecha_solicitud.desc()).limit(200).all()
    return render_template("examenes/index.html", examenes=examenes, estado=estado, estados=ESTADOS_EXAMEN)


@examenes_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@role_required("administrador", "medico")
def crear():
    pacientes = Paciente.query.order_by(Paciente.apellidos).all()
    medicos = Medico.query.order_by(Medico.apellidos).all()
    if request.method == "POST":
        e = Examen()
        e.paciente_id = request.form.get("paciente_id", type=int)
        e.medico_id = request.form.get("medico_id", type=int)
        e.tipo = request.form.get("tipo", "").strip()
        e.descripcion = request.form.get("descripcion", "").strip() or None
        if not e.paciente_id or not e.medico_id or not e.tipo:
            flash("Paciente, medico y tipo de examen son obligatorios.", "danger")
        else:
            db.session.add(e)
            db.session.commit()
            flash("Examen solicitado.", "success")
            return redirect(url_for("examenes.index"))
    return render_template("examenes/form.html", e=Examen(), pacientes=pacientes, medicos=medicos, modo="crear")


@examenes_bp.route("/<int:eid>/resultado", methods=["GET", "POST"])
@login_required
@role_required("administrador", "medico")
def resultado(eid):
    e = db.session.get(Examen, eid) or abort(404)
    if request.method == "POST":
        e.resultado = request.form.get("resultado", "").strip() or None
        e.estado = request.form.get("estado") if request.form.get("estado") in ESTADOS_EXAMEN else e.estado
        if e.estado == "completado" and not e.fecha_resultado:
            e.fecha_resultado = datetime.utcnow()
        db.session.commit()
        flash("Resultado registrado.", "success")
        return redirect(url_for("examenes.index"))
    return render_template("examenes/resultado.html", e=e, estados=ESTADOS_EXAMEN)
