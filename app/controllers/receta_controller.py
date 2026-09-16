from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    send_file,
)
from flask_login import login_required

from app.extensions import db
from app.models.receta import Receta
from app.models.paciente import Paciente
from app.models.medico import Medico
from app.models.historial import HistorialClinico
from app.services.pdf_service import receta_pdf
from app.utils.decorators import role_required

recetas_bp = Blueprint("recetas", __name__, url_prefix="/recetas")

CLINICOS = ("administrador", "medico")


@recetas_bp.route("/")
@login_required
@role_required("administrador", "medico", "recepcionista")
def index():
    recetas = Receta.query.order_by(Receta.fecha.desc()).limit(200).all()
    return render_template("recetas/index.html", recetas=recetas)


@recetas_bp.route("/<int:rid>")
@login_required
@role_required("administrador", "medico", "recepcionista", "paciente")
def detalle(rid):
    r = db.session.get(Receta, rid) or abort(404)
    return render_template("recetas/detalle.html", r=r)


@recetas_bp.route("/nueva", methods=["GET", "POST"])
@login_required
@role_required(*CLINICOS)
def crear():
    pacientes = Paciente.query.order_by(Paciente.apellidos).all()
    medicos = Medico.query.order_by(Medico.apellidos).all()
    historial_id = request.args.get("historial_id", type=int)

    if request.method == "POST":
        r = Receta()
        r.paciente_id = request.form.get("paciente_id", type=int)
        r.medico_id = request.form.get("medico_id", type=int)
        r.historial_id = request.form.get("historial_id", type=int) or None
        r.diagnostico = request.form.get("diagnostico", "").strip() or None
        r.indicaciones = request.form.get("indicaciones", "").strip() or None

        meds = []
        nombres = request.form.getlist("med_nombre")
        dosis = request.form.getlist("med_dosis")
        frec = request.form.getlist("med_frecuencia")
        dur = request.form.getlist("med_duracion")
        for i, nom in enumerate(nombres):
            if nom.strip():
                meds.append({
                    "medicamento": nom.strip(),
                    "dosis": dosis[i].strip() if i < len(dosis) else "",
                    "frecuencia": frec[i].strip() if i < len(frec) else "",
                    "duracion": dur[i].strip() if i < len(dur) else "",
                })
        r.medicamentos = meds

        if not r.paciente_id or not r.medico_id or not meds:
            flash("Paciente, medico y al menos un medicamento son obligatorios.", "danger")
        else:
            db.session.add(r)
            db.session.commit()
            flash("Receta emitida.", "success")
            return redirect(url_for("recetas.detalle", rid=r.id))

    h = db.session.get(HistorialClinico, historial_id) if historial_id else None
    return render_template(
        "recetas/form.html", r=Receta(historial_id=historial_id), pacientes=pacientes,
        medicos=medicos, historial=h,
    )


@recetas_bp.route("/<int:rid>/pdf")
@login_required
@role_required("administrador", "medico", "recepcionista", "paciente")
def descargar_pdf(rid):
    r = db.session.get(Receta, rid) or abort(404)
    buffer = receta_pdf(r)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"receta_{r.id}.pdf",
    )
