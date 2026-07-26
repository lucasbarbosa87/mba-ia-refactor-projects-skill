import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils.exceptions import AppException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppException)
    def handle_app_exception(error):
        return jsonify({"erro": error.message, "sucesso": False}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return (
            jsonify({"erro": error.description, "sucesso": False}),
            error.code,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        logger.exception("Erro interno não tratado")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
