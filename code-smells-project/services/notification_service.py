import logging

from utils.constants import OrderStatus

logger = logging.getLogger(__name__)


class NotificationService:
    """Encapsula os efeitos colaterais de notificação (email, SMS, push).

    Aqui os canais são simulados via logging; substituir por integrações reais."""

    def notify_order_created(self, usuario_id, pedido_id):
        logger.info("Email: pedido %s criado para usuário %s", pedido_id, usuario_id)
        logger.info("SMS: seu pedido %s foi recebido", pedido_id)
        logger.info("Push: novo pedido %s recebido pelo sistema", pedido_id)

    def notify_status_change(self, pedido_id, novo_status):
        if novo_status == OrderStatus.APROVADO.value:
            logger.info("Pedido %s aprovado! Preparar envio.", pedido_id)
        elif novo_status == OrderStatus.CANCELADO.value:
            logger.info("Pedido %s cancelado. Devolver estoque.", pedido_id)
