from flask import Blueprint, jsonify, request

from controllers.order_controller import OrderController
from utils.exceptions import ValidationError

order_bp = Blueprint("pedidos", __name__)
controller = OrderController()


@order_bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    dados = request.get_json()
    if not dados:
        raise ValidationError("Dados inválidos")

    resultado = controller.create_order(dados.get("usuario_id"), dados.get("itens", []))
    return (
        jsonify(
            {
                "dados": resultado,
                "sucesso": True,
                "mensagem": "Pedido criado com sucesso",
            }
        ),
        201,
    )


@order_bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    pedidos = controller.list_all_orders()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


@order_bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    pedidos = controller.list_user_orders(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


@order_bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    dados = request.get_json() or {}
    controller.update_status(pedido_id, dados.get("status", ""))
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200


@order_bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    relatorio = controller.sales_report()
    return jsonify({"dados": relatorio, "sucesso": True}), 200
