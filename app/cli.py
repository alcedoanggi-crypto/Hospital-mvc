"""Comandos de linea: flask --app run.py <comando>"""
from datetime import datetime, timedelta
from decimal import Decimal

import click

from app.extensions import db


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        """Crea todas las tablas (alternativa rapida a las migraciones)."""
        db.create_all()
        click.echo("Tablas creadas.")

    @app.cli.command("seed")
    def seed():
        """Carga datos de demostracion."""
        from app.models import (
            Usuario,
            Especialidad,
            Medico,
            Paciente,
            Cita,
            HistorialClinico,
            Receta,
            Factura,
        )

        db.create_all()

        if Usuario.query.first():
            click.echo("La base ya tiene datos. Aborta el seed.")
            return

        # Usuarios
        admin = Usuario(nombre="Ana", apellido="Torres", email="admin@hospital.test", rol="administrador")
        admin.set_password("admin123")
        recep = Usuario(nombre="Rosa", apellido="Diaz", email="recepcion@hospital.test", rol="recepcionista")
        recep.set_password("recep123")
        u_med = Usuario(nombre="Carlos", apellido="Mendoza", email="medico@hospital.test", rol="medico")
        u_med.set_password("medico123")
        u_pac = Usuario(nombre="Luis", apellido="Ramos", email="paciente@hospital.test", rol="paciente")
        u_pac.set_password("paciente123")
        db.session.add_all([admin, recep, u_med, u_pac])
        db.session.flush()

        # Especialidades
        esp_data = [
            ("Medicina General", "Atencion primaria", 60),
            ("Cardiologia", "Corazon y sistema circulatorio", 120),
            ("Pediatria", "Salud infantil", 90),
            ("Dermatologia", "Piel", 100),
            ("Traumatologia", "Huesos y articulaciones", 110),
        ]
        esps = [Especialidad(nombre=n, descripcion=d, precio_consulta=Decimal(p)) for n, d, p in esp_data]
        db.session.add_all(esps)
        db.session.flush()

        # Medicos
        med = Medico(usuario_id=u_med.id, especialidad_id=esps[1].id, nombres="Carlos",
                     apellidos="Mendoza", colegiatura="CMP-10234", telefono="999888777")
        med2 = Medico(especialidad_id=esps[2].id, nombres="Elena", apellidos="Quispe",
                      colegiatura="CMP-20455", telefono="988777666")
        db.session.add_all([med, med2])
        db.session.flush()

        # Pacientes
        pac = Paciente(usuario_id=u_pac.id, nombres="Luis", apellidos="Ramos", dni="45781233",
                       fecha_nacimiento=datetime(1990, 5, 12).date(), sexo="M", telefono="977666555",
                       email="paciente@hospital.test", tipo_sangre="O+", alergias="Penicilina")
        pac2 = Paciente(nombres="Maria", apellidos="Flores", dni="40122988",
                        fecha_nacimiento=datetime(1985, 9, 3).date(), sexo="F", telefono="966555444",
                        tipo_sangre="A+", alergias="Ninguna conocida")
        db.session.add_all([pac, pac2])
        db.session.flush()

        # Citas (algunas atendidas, otras programadas / canceladas)
        base = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
        citas = [
            Cita(paciente_id=pac.id, medico_id=med.id, fecha_hora=base - timedelta(days=3),
                 motivo="Control de presion", estado="atendida"),
            Cita(paciente_id=pac2.id, medico_id=med2.id, fecha_hora=base - timedelta(days=2, hours=-2),
                 motivo="Chequeo pediatrico", estado="atendida"),
            Cita(paciente_id=pac.id, medico_id=med.id, fecha_hora=base - timedelta(days=1),
                 motivo="Dolor toracico", estado="cancelada"),
            Cita(paciente_id=pac2.id, medico_id=med.id, fecha_hora=base + timedelta(days=1, hours=1),
                 motivo="Seguimiento", estado="programada"),
            Cita(paciente_id=pac.id, medico_id=med2.id, fecha_hora=base + timedelta(days=2),
                 motivo="Consulta general", estado="programada"),
        ]
        db.session.add_all(citas)
        db.session.flush()

        # Historial + receta para la primera cita atendida
        h = HistorialClinico(paciente_id=pac.id, medico_id=med.id, cita_id=citas[0].id,
                             motivo_consulta="Control de presion",
                             diagnostico="Hipertension arterial leve",
                             tratamiento="Dieta baja en sodio, actividad fisica",
                             alergias="Penicilina")
        db.session.add(h)
        db.session.flush()
        db.session.add(Receta(paciente_id=pac.id, medico_id=med.id, historial_id=h.id,
                              diagnostico="Hipertension arterial leve",
                              indicaciones="Tomar con el desayuno. Controlar presion 2 veces por semana.",
                              medicamentos=[
                                  {"medicamento": "Enalapril 10mg", "dosis": "1 tableta",
                                   "frecuencia": "cada 24h", "duracion": "30 dias"},
                              ]))

        # Facturas para citas atendidas
        for c in citas[:2]:
            precio = float(c.medico.especialidad.precio_consulta)
            f = Factura(paciente_id=c.paciente_id, cita_id=c.id, numero=f"F-{c.id:05d}",
                        estado="pagada", metodo_pago="tarjeta",
                        detalle=[{"concepto": f"Consulta {c.medico.especialidad.nombre}",
                                  "cantidad": 1, "precio": precio}])
            f.recalcular()
            db.session.add(f)

        db.session.commit()
        click.echo("Seed completo.")
        click.echo("  admin@hospital.test / admin123")
        click.echo("  medico@hospital.test / medico123")
        click.echo("  recepcion@hospital.test / recep123")
        click.echo("  paciente@hospital.test / paciente123")
