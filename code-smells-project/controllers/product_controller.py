import logging

from models.product import Product
from utils.exceptions import NotFoundError
from utils.validators import validate_product_data

logger = logging.getLogger(__name__)


class ProductController:
    def list_products(self):
        produtos = Product.all()
        logger.info("Listando %s produtos", len(produtos))
        return produtos

    def search_products(self, termo, categoria, preco_min, preco_max):
        return Product.search(termo, categoria, preco_min, preco_max)

    def get_product(self, produto_id):
        produto = Product.find_by_id(produto_id)
        if not produto:
            raise NotFoundError("Produto")
        return produto

    def create_product(self, dados):
        validate_product_data(dados, full=True)
        produto_id = Product.create(
            dados["nome"],
            dados.get("descricao", ""),
            dados["preco"],
            dados["estoque"],
            dados.get("categoria", "geral"),
        )
        logger.info("Produto criado com ID: %s", produto_id)
        return produto_id

    def update_product(self, produto_id, dados):
        if not Product.find_by_id(produto_id):
            raise NotFoundError("Produto")
        validate_product_data(dados, full=False)
        Product.update(
            produto_id,
            dados["nome"],
            dados.get("descricao", ""),
            dados["preco"],
            dados["estoque"],
            dados.get("categoria", "geral"),
        )

    def delete_product(self, produto_id):
        if not Product.find_by_id(produto_id):
            raise NotFoundError("Produto")
        Product.delete(produto_id)
        logger.info("Produto %s deletado", produto_id)
