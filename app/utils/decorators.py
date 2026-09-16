"""Control de acceso basado en roles."""
from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*roles):
    """Permite el acceso solo a los roles indicados.

    Uso: @role_required("administrador", "recepcionista")
    """

    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.rol not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapper

    return decorator
