"""Error handling centralizado.

Converte exceções de aplicação (AppException) e erros HTTP padrão em
respostas JSON consistentes, com logging estruturado para erros internos.
"""
import logging

from flask import jsonify

from exceptions import AppException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppException)
    def handle_app_exception(error):
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({'error': 'Método não permitido'}), 405

    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.exception('Erro interno do servidor')
        return jsonify({'error': 'Erro interno'}), 500
