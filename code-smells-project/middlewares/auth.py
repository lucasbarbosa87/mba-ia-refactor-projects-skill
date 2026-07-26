from functools import wraps

from flask import request

from config.settings import Config
from utils.exceptions import UnauthorizedError


def admin_required(func):
    """Exige o header X-Admin-Token válido. Se ADMIN_TOKEN não estiver
    configurado, o acesso administrativo fica desabilitado."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-Admin-Token")
        if not Config.ADMIN_TOKEN or token != Config.ADMIN_TOKEN:
            raise UnauthorizedError("Acesso administrativo negado")
        return func(*args, **kwargs)

    return wrapper
