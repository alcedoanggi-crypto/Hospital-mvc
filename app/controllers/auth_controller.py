from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db
from app.models.usuario import Usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = Usuario.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Credenciales invalidas.", "danger")
        elif not user.activo:
            flash("Tu cuenta esta desactivada. Contacta al administrador.", "warning")
        else:
            login_user(user, remember=bool(request.form.get("remember")))
            flash(f"Bienvenido/a, {user.nombre}.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesion cerrada.", "info")
    return redirect(url_for("auth.login"))
