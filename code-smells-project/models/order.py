from models.base import get_connection
from utils.constants import OrderStatus


class Order:
    @staticmethod
    def _pedido_dict(row):
        return {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": [],
        }

    @staticmethod
    def _load_itens(conn, pedido_ids):
        """Carrega os itens de vários pedidos em UMA query (evita N+1)."""
        if not pedido_ids:
            return {}
        placeholders = ",".join("?" * len(pedido_ids))
        rows = conn.execute(
            f"""
            SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario,
                   p.nome AS produto_nome
            FROM itens_pedido ip
            LEFT JOIN produtos p ON p.id = ip.produto_id
            WHERE ip.pedido_id IN ({placeholders})
            """,
            pedido_ids,
        ).fetchall()

        grouped = {}
        for row in rows:
            grouped.setdefault(row["pedido_id"], []).append(
                {
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] or "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                }
            )
        return grouped

    @classmethod
    def _list_with_itens(cls, where="", params=None):
        conn = get_connection()
        try:
            rows = conn.execute(
                f"SELECT * FROM pedidos {where}", params or []
            ).fetchall()
            pedidos = [cls._pedido_dict(row) for row in rows]
            itens_por_pedido = cls._load_itens(conn, [p["id"] for p in pedidos])
            for pedido in pedidos:
                pedido["itens"] = itens_por_pedido.get(pedido["id"], [])
            return pedidos
        finally:
            conn.close()

    @classmethod
    def all_with_itens(cls):
        return cls._list_with_itens()

    @classmethod
    def by_user_with_itens(cls, usuario_id):
        return cls._list_with_itens("WHERE usuario_id = ?", [usuario_id])

    @classmethod
    def find_by_id(cls, pedido_id):
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM pedidos WHERE id = ?", [pedido_id]
            ).fetchone()
        finally:
            conn.close()

    @classmethod
    def create(cls, usuario_id, total, itens):
        """Cria pedido, itens e baixa de estoque numa única transação.

        `itens` é uma lista de dicts com produto_id, quantidade e preco_unitario."""
        conn = get_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
                [usuario_id, OrderStatus.PENDENTE.value, total],
            )
            pedido_id = cursor.lastrowid
            for item in itens:
                conn.execute(
                    "INSERT INTO itens_pedido "
                    "(pedido_id, produto_id, quantidade, preco_unitario) "
                    "VALUES (?, ?, ?, ?)",
                    [
                        pedido_id,
                        item["produto_id"],
                        item["quantidade"],
                        item["preco_unitario"],
                    ],
                )
                conn.execute(
                    "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                    [item["quantidade"], item["produto_id"]],
                )
            conn.commit()
            return pedido_id
        finally:
            conn.close()

    @classmethod
    def update_status(cls, pedido_id, novo_status):
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE pedidos SET status = ? WHERE id = ?",
                [novo_status, pedido_id],
            )
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def count(cls):
        conn = get_connection()
        try:
            return conn.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
        finally:
            conn.close()

    @classmethod
    def sales_aggregates(cls):
        """Agregados brutos para o relatório de vendas (sem regra de negócio)."""
        conn = get_connection()
        try:
            total_pedidos = conn.execute(
                "SELECT COUNT(*) FROM pedidos"
            ).fetchone()[0]
            faturamento = conn.execute(
                "SELECT SUM(total) FROM pedidos"
            ).fetchone()[0] or 0
            por_status = {}
            for status in (
                OrderStatus.PENDENTE,
                OrderStatus.APROVADO,
                OrderStatus.CANCELADO,
            ):
                por_status[status.value] = conn.execute(
                    "SELECT COUNT(*) FROM pedidos WHERE status = ?",
                    [status.value],
                ).fetchone()[0]
            return total_pedidos, faturamento, por_status
        finally:
            conn.close()
