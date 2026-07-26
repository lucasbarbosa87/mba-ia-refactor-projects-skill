import re

from utils.constants import CATEGORIAS_VALIDAS, NOME_MAX_LEN, NOME_MIN_LEN
from utils.exceptions import ValidationError

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_product_data(dados, full=True):
    """Valida payload de produto. `full=False` pula checagens de nome/categoria
    (usado no update, preservando o comportamento original)."""
    if not dados:
        raise ValidationError("Dados inválidos")
    if "nome" not in dados:
        raise ValidationError("Nome é obrigatório")
    if "preco" not in dados:
        raise ValidationError("Preço é obrigatório")
    if "estoque" not in dados:
        raise ValidationError("Estoque é obrigatório")

    if dados["preco"] < 0:
        raise ValidationError("Preço não pode ser negativo")
    if dados["estoque"] < 0:
        raise ValidationError("Estoque não pode ser negativo")

    if full:
        nome = dados["nome"]
        if len(nome) < NOME_MIN_LEN:
            raise ValidationError("Nome muito curto")
        if len(nome) > NOME_MAX_LEN:
            raise ValidationError("Nome muito longo")

        categoria = dados.get("categoria", "geral")
        if categoria not in CATEGORIAS_VALIDAS:
            raise ValidationError(
                "Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS)
            )


def validate_user_data(nome, email, senha):
    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if not EMAIL_REGEX.match(email):
        raise ValidationError("Email inválido")
    if len(senha) < 6:
        raise ValidationError("Senha deve ter no mínimo 6 caracteres")
