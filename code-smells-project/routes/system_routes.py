from flask import Blueprint, jsonify, request

from controllers.system_controller import SystemController
from middlewares.auth import admin_required
from utils.exceptions import ValidationError

system_bp = Blueprint("system", __name__)
controller = SystemController()


@system_bp.route("/", methods=["GET"])
def index():
    return jsonify(controller.index())


@system_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify(controller.health()), 200


@system_bp.route("/admin/reset-db", methods=["POST"])
@admin_required
def reset_database():
    controller.reset_database()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


@system_bp.route("/admin/query", methods=["POST"])
@admin_required
def executar_query():
    dados = request.get_json() or {}
    query = dados.get("sql", "")
    if not query:
        raise ValidationError("Query não informada")

    rows, is_select = controller.run_query(query)
    if is_select:
        return jsonify({"dados": rows, "sucesso": True}), 200
    return jsonify({"mensagem": "Query executada", "sucesso": True}), 200
