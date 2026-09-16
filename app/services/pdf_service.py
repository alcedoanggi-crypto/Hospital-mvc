"""Generacion de PDF con ReportLab (recetas medicas descargables)."""
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

CELESTE = colors.HexColor("#38BDF8")
VERDE = colors.HexColor("#22C55E")
GRIS = colors.HexColor("#94A3B8")


def receta_pdf(receta):
    """Devuelve un BytesIO con el PDF de la receta."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        title=f"Receta {receta.id}",
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], textColor=CELESTE, fontSize=20)
    label = ParagraphStyle("label", parent=styles["Normal"], textColor=GRIS, fontSize=9)
    normal = styles["Normal"]

    elems = []
    elems.append(Paragraph("RECETA MEDICA DIGITAL", h1))
    elems.append(Spacer(1, 4 * mm))

    med = receta.medico
    pac = receta.paciente
    cab = [
        [Paragraph("Medico", label), Paragraph(med.nombre_completo if med else "-", normal),
         Paragraph("Fecha", label), Paragraph(receta.fecha.strftime("%d/%m/%Y %H:%M"), normal)],
        [Paragraph("Colegiatura", label), Paragraph(getattr(med, "colegiatura", "-"), normal),
         Paragraph("Especialidad", label),
         Paragraph(med.especialidad.nombre if med and med.especialidad else "-", normal)],
        [Paragraph("Paciente", label), Paragraph(pac.nombre_completo if pac else "-", normal),
         Paragraph("DNI", label), Paragraph(getattr(pac, "dni", "-"), normal)],
    ]
    t = Table(cab, colWidths=[25 * mm, 60 * mm, 25 * mm, 60 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, GRIS),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 6 * mm))

    if receta.diagnostico:
        elems.append(Paragraph("Diagnostico", label))
        elems.append(Paragraph(receta.diagnostico, normal))
        elems.append(Spacer(1, 4 * mm))

    elems.append(Paragraph("Medicamentos indicados", label))
    filas = [["Medicamento", "Dosis", "Frecuencia", "Duracion"]]
    for m in receta.medicamentos or []:
        filas.append([
            m.get("medicamento", ""),
            m.get("dosis", ""),
            m.get("frecuencia", ""),
            m.get("duracion", ""),
        ])
    tabla_med = Table(filas, colWidths=[65 * mm, 35 * mm, 35 * mm, 35 * mm])
    tabla_med.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CELESTE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, GRIS),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ]))
    elems.append(tabla_med)
    elems.append(Spacer(1, 6 * mm))

    if receta.indicaciones:
        elems.append(Paragraph("Indicaciones", label))
        elems.append(Paragraph(receta.indicaciones.replace("\n", "<br/>"), normal))

    elems.append(Spacer(1, 20 * mm))
    firma = Table([["_" * 35], [Paragraph("Firma y sello del medico", label)]], colWidths=[80 * mm])
    firma.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    elems.append(firma)

    doc.build(elems)
    buffer.seek(0)
    return buffer
