import logging

from models.user import User
from utils.exceptions import NotFoundError, UnauthorizedError, ValidationError
from utils.validators import validate_user_data

logger = logging.getLogger(__name__)


class UserController:
    def list_users(self):
        return User.all()

    def get_user(self, usuario_id):
        usuario = User.find_by_id(usuario_id)
        if not usuario:
            raise NotFoundError("Usuário")
        return usuario

    def create_user(self, dados):
        if not dados:
            raise ValidationError("Dados inválidos")
        nome = dados.get("nome", "")
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        validate_user_data(nome, email, senha)

        if User.find_by_email(email):
            raise ValidationError("Email já cadastrado")

        usuario_id = User.create(nome, email, senha)
        logger.info("Usuário criado: %s", email)
        return usuario_id

    def login(self, dados):
        email = (dados or {}).get("email", "")
        senha = (dados or {}).get("senha", "")
        if not email or not senha:
            raise ValidationError("Email e senha são obrigatórios")

        usuario = User.verify_login(email, senha)
        if not usuario:
            logger.info("Login falhou: %s", email)
            raise UnauthorizedError("Email ou senha inválidos")

        logger.info("Login bem-sucedido: %s", email)
        return usuario
