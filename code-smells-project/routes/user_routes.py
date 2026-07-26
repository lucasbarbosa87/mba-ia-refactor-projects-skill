from flask import Blueprint, jsonify, request

from controllers.user_controller import UserController

user_bp = Blueprint("usuarios", __name__)
controller = UserController()


@user_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = controller.list_users()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


@user_bp.route("/usuarios/<int:id>", methods=["GET"])
def buscar_usuario(id):
    usuario = controller.get_user(id)
    return jsonify({"dados": usuario, "sucesso": True}), 200


@user_bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    usuario_id = controller.create_user(request.get_json())
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


@user_bp.route("/login", methods=["POST"])
def login():
    usuario = controller.login(request.get_json())
    return (
        jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}),
        200,
    )
