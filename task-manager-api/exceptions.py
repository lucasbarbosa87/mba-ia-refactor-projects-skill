"""Exceções de aplicação para tratamento de erros centralizado.

Controllers levantam estas exceções; o error handler central (registrado
em middlewares/error_handler.py) as converte em respostas HTTP com o
status code adequado, mantendo as rotas limpas.
"""


class AppException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class ValidationError(AppException):
    status_code = 400


class NotFoundError(AppException):
    status_code = 404


class ConflictError(AppException):
    status_code = 409


class UnauthorizedError(AppException):
    status_code = 401


class ForbiddenError(AppException):
    status_code = 403
