class AppException(Exception):
    """Exceção base da aplicação, tratada pelo error handler centralizado."""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(AppException):
    def __init__(self, message):
        super().__init__(message, 400)


class NotFoundError(AppException):
    def __init__(self, resource):
        super().__init__(f"{resource} não encontrado", 404)


class UnauthorizedError(AppException):
    def __init__(self, message="Não autorizado"):
        super().__init__(message, 401)
