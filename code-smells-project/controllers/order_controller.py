from models.order import Order
from models.product import Product
from services.notification_service import NotificationService
from utils.constants import DISCOUNT_TIERS, OrderStatus
from utils.exceptions import NotFoundError, ValidationError


class OrderController:
    def __init__(self, notification_service=None):
        self.notifications = notification_service or NotificationService()

    def create_order(self, usuario_id, itens):
        if not usuario_id:
            raise ValidationError("Usuario ID é obrigatório")
        if not itens:
            raise ValidationError("Pedido deve ter pelo menos 1 item")

        total = 0
        linhas = []
        for item in itens:
            produto = Product.find_by_id(item["produto_id"])
            if produto is None:
                raise ValidationError(
                    "Produto " + str(item["produto_id"]) + " não encontrado"
                )
            if produto["estoque"] < item["quantidade"]:
                raise ValidationError("Estoque insuficiente para " + produto["nome"])
            total += produto["preco"] * item["quantidade"]
            linhas.append(
                {
                    "produto_id": item["produto_id"],
                    "quantidade": item["quantidade"],
                    "preco_unitario": produto["preco"],
                }
            )

        pedido_id = Order.create(usuario_id, total, linhas)
        self.notifications.notify_order_created(usuario_id, pedido_id)
        return {"pedido_id": pedido_id, "total": total}

    def list_all_orders(self):
        return Order.all_with_itens()

    def list_user_orders(self, usuario_id):
        return Order.by_user_with_itens(usuario_id)

    def update_status(self, pedido_id, novo_status):
        if novo_status not in OrderStatus.values():
            raise ValidationError("Status inválido")
        if not Order.find_by_id(pedido_id):
            raise NotFoundError("Pedido")

        Order.update_status(pedido_id, novo_status)
        self.notifications.notify_status_change(pedido_id, novo_status)

    def sales_report(self):
        total_pedidos, faturamento, por_status = Order.sales_aggregates()

        desconto = 0
        for minimo, percentual in DISCOUNT_TIERS:
            if faturamento > minimo:
                desconto = faturamento * percentual
                break

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": por_status[OrderStatus.PENDENTE.value],
            "pedidos_aprovados": por_status[OrderStatus.APROVADO.value],
            "pedidos_cancelados": por_status[OrderStatus.CANCELADO.value],
            "ticket_medio": (
                round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0
            ),
        }
