from datetime import datetime, timedelta

from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from app.extensions import db
from app.models.cita import Cita
from app.models.paciente import Paciente
from app.models.factura import Factura

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    hoy = datetime.utcnow().date()
    inicio_dia = datetime.combine(hoy, datetime.min.time())
    fin_dia = inicio_dia + timedelta(days=1)
    hace_30 = inicio_dia - timedelta(days=30)

    citas_hoy = Cita.query.filter(
        Cita.fecha_hora >= inicio_dia, Cita.fecha_hora < fin_dia
    ).count()

    pacientes_nuevos = Paciente.query.filter(Paciente.creado_en >= hace_30).count()

    ingresos_mes = (
        db.session.query(func.coalesce(func.sum(Factura.total), 0))
        .filter(Factura.estado == "pagada", Factura.fecha >= hace_30)
        .scalar()
    )

    citas_pendientes = Cita.query.filter(
        Cita.estado == "programada", Cita.fecha_hora >= datetime.utcnow()
    ).count()

    proximas = (
        Cita.query.filter(
            Cita.estado == "programada", Cita.fecha_hora >= datetime.utcnow()
        )
        .order_by(Cita.fecha_hora.asc())
        .limit(6)
        .all()
    )

    kpis = {
        "citas_hoy": citas_hoy,
        "pacientes_nuevos": pacientes_nuevos,
        "ingresos_mes": float(ingresos_mes or 0),
        "citas_pendientes": citas_pendientes,
        "total_pacientes": Paciente.query.count(),
    }

    return render_template("dashboard/index.html", kpis=kpis, proximas=proximas)
