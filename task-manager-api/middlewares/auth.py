"""Autenticação baseada em tokens assinados.

Substitui o antigo "fake-jwt-token-<id>" por tokens assinados com o
SECRET_KEY da aplicação (via itsdangerous, já disponível com o Flask).

O decorator `token_required` permite proteger rotas sensíveis/admin.
Ele NÃO é aplicado globalmente para preservar os contratos públicos
existentes da API; use-o nas rotas que precisam de autenticação.
"""
from functools import wraps

from flask import current_app, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from exceptions import UnauthorizedError

TOKEN_MAX_AGE_SECONDS = 24 * 60 * 60  # 24h


def _serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='auth-token')


def generate_token(user_id):
    """Gera um token assinado para o usuário autenticado."""
    return _serializer().dumps({'user_id': user_id})


def verify_token(token, max_age=TOKEN_MAX_AGE_SECONDS):
    """Retorna o user_id do token válido, ou None se inválido/expirado."""
    try:
        data = _serializer().loads(token, max_age=max_age)
        return data.get('user_id')
    except (BadSignature, SignatureExpired):
        return None


def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header[7:] if auth_header.startswith('Bearer ') else auth_header
        user_id = verify_token(token) if token else None
        if user_id is None:
            raise UnauthorizedError('Token inválido ou ausente')
        request.user_id = user_id
        return fn(*args, **kwargs)

    return wrapper
