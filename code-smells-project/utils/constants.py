from enum import Enum


class OrderStatus(str, Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"

    @classmethod
    def values(cls):
        return [status.value for status in cls]


class UserRole(str, Enum):
    CLIENTE = "cliente"
    ADMIN = "admin"


CATEGORIAS_VALIDAS = [
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
]

NOME_MIN_LEN = 2
NOME_MAX_LEN = 200

# Faixas de desconto do relatório de vendas: (faturamento_mínimo, percentual).
# Avaliadas da maior para a menor.
DISCOUNT_TIERS = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]
