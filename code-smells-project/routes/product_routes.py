from flask import Blueprint, jsonify, request

from controllers.product_controller import ProductController

product_bp = Blueprint("produtos", __name__)
controller = ProductController()


@product_bp.route("/produtos", methods=["GET"])
def listar_produtos():
    produtos = controller.list_products()
    return jsonify({"dados": produtos, "sucesso": True}), 200


@product_bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", type=float)
    preco_max = request.args.get("preco_max", type=float)

    resultados = controller.search_products(termo, categoria, preco_min, preco_max)
    return (
        jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}),
        200,
    )


@product_bp.route("/produtos/<int:id>", methods=["GET"])
def buscar_produto(id):
    produto = controller.get_product(id)
    return jsonify({"dados": produto, "sucesso": True}), 200


@product_bp.route("/produtos", methods=["POST"])
def criar_produto():
    produto_id = controller.create_product(request.get_json())
    return (
        jsonify(
            {"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}
        ),
        201,
    )


@product_bp.route("/produtos/<int:id>", methods=["PUT"])
def atualizar_produto(id):
    controller.update_product(id, request.get_json())
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


@product_bp.route("/produtos/<int:id>", methods=["DELETE"])
def deletar_produto(id):
    controller.delete_product(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
