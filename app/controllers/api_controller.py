"""Endpoints JSON para Chart.js, FullCalendar y busqueda en vivo."""
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import func, or_

from app.extensions import db
from app.models.cita import Cita
from app.models.paciente import Paciente
from app.models.medico import Medico
from app.models.especialidad import Especialidad
from app.models.factura import Factura

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/dashboard/stats")
@login_required
def dashboard_stats():
    hace_180 = datetime.utcnow() - timedelta(days=180)

    def clave_mes(fecha):
        return fecha.strftime("%Y-%m")

    # --- Citas atendidas vs canceladas por mes (bucketing en Python: portable) ---
    citas = Cita.query.filter(Cita.fecha_hora >= hace_180).all()
    meses = sorted({clave_mes(c.fecha_hora) for c in citas})
    atendidas = {m: 0 for m in meses}
    canceladas = {m: 0 for m in meses}
    for c in citas:
        m = clave_mes(c.fecha_hora)
        if c.estado == "atendida":
            atendidas[m] += 1
        elif c.estado in ("cancelada", "no_asistio"):
            canceladas[m] += 1

    # --- Especialidades mas demandadas ---
    esp_rows = (
        db.session.query(Especialidad.nombre, func.count(Cita.id))
        .join(Medico, Medico.especialidad_id == Especialidad.id)
        .join(Cita, Cita.medico_id == Medico.id)
        .group_by(Especialidad.nombre)
        .order_by(func.count(Cita.id).desc())
        .limit(6)
        .all()
    )

    # --- Ingresos por mes (facturas pagadas) ---
    facturas = Factura.query.filter(
        Factura.estado == "pagada", Factura.fecha >= hace_180
    ).all()
    ingresos = {}
    for f in facturas:
        ingresos[clave_mes(f.fecha)] = ingresos.get(clave_mes(f.fecha), 0) + float(f.total)
    meses_ing = sorted(ingresos)

    return jsonify(
        {
            "citas": {
                "labels": meses,
                "atendidas": [atendidas[m] for m in meses],
                "canceladas": [canceladas[m] for m in meses],
            },
            "especialidades": {
                "labels": [r[0] for r in esp_rows],
                "data": [r[1] for r in esp_rows],
            },
            "ingresos": {
                "labels": meses_ing,
                "data": [round(ingresos[m], 2) for m in meses_ing],
            },
        }
    )


@api_bp.route("/citas")
@login_required
def citas_calendario():
    """Eventos para FullCalendar."""
    q = Cita.query
    start = request.args.get("start")
    end = request.args.get("end")
    if start:
        q = q.filter(Cita.fecha_hora >= datetime.fromisoformat(start.replace("Z", "")))
    if end:
        q = q.filter(Cita.fecha_hora <= datetime.fromisoformat(end.replace("Z", "")))

    colores = {
        "programada": "#38BDF8",
        "atendida": "#22C55E",
        "cancelada": "#94A3B8",
        "no_asistio": "#F97316",
    }
    eventos = []
    for c in q.all():
        eventos.append(
            {
                "id": c.id,
                "title": f"{c.paciente.nombre_completo} - {c.medico.nombre_completo}",
                "start": c.fecha_hora.isoformat(),
                "end": (c.fecha_hora + timedelta(minutes=c.duracion_min or 30)).isoformat(),
                "color": colores.get(c.estado, "#38BDF8"),
                "extendedProps": {"estado": c.estado, "motivo": c.motivo or ""},
                "url": f"/citas/{c.id}",
            }
        )
    return jsonify(eventos)


@api_bp.route("/pacientes/buscar")
@login_required
def buscar_pacientes():
    term = request.args.get("q", "").strip()
    if not term:
        return jsonify([])
    like = f"%{term}%"
    pacientes = (
        Paciente.query.filter(
            or_(
                Paciente.nombres.ilike(like),
                Paciente.apellidos.ilike(like),
                Paciente.dni.ilike(like),
            )
        )
        .limit(10)
        .all()
    )
    return jsonify(
        [
            {
                "id": p.id,
                "nombre": p.nombre_completo,
                "dni": p.dni,
                "telefono": p.telefono,
            }
            for p in pacientes
        ]
    )
