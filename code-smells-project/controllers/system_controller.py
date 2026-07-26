from config.settings import Config
from models import base
from models.order import Order
from models.product import Product
from models.user import User


class SystemController:
    def index(self):
        return {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": Config.VERSAO,
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }

    def health(self):
        return {
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": Product.count(),
                "usuarios": User.count(),
                "pedidos": Order.count(),
            },
            "versao": Config.VERSAO,
            "ambiente": Config.AMBIENTE,
        }

    def reset_database(self):
        base.reset_all()

    def run_query(self, sql):
        return base.execute_raw(sql)
