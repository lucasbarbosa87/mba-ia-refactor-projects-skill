from models.base import get_connection


class Product:
    @staticmethod
    def _to_dict(row):
        if row is None:
            return None
        return {
            "id": row["id"],
            "nome": row["nome"],
            "descricao": row["descricao"],
            "preco": row["preco"],
            "estoque": row["estoque"],
            "categoria": row["categoria"],
            "ativo": row["ativo"],
            "criado_em": row["criado_em"],
        }

    @classmethod
    def all(cls):
        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM produtos").fetchall()
            return [cls._to_dict(row) for row in rows]
        finally:
            conn.close()

    @classmethod
    def find_by_id(cls, produto_id):
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM produtos WHERE id = ?", [produto_id]
            ).fetchone()
            return cls._to_dict(row)
        finally:
            conn.close()

    @classmethod
    def create(cls, nome, descricao, preco, estoque, categoria):
        conn = get_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
                "VALUES (?, ?, ?, ?, ?)",
                [nome, descricao, preco, estoque, categoria],
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @classmethod
    def update(cls, produto_id, nome, descricao, preco, estoque, categoria):
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, "
                "estoque = ?, categoria = ? WHERE id = ?",
                [nome, descricao, preco, estoque, categoria, produto_id],
            )
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def delete(cls, produto_id):
        conn = get_connection()
        try:
            conn.execute("DELETE FROM produtos WHERE id = ?", [produto_id])
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def search(cls, termo=None, categoria=None, preco_min=None, preco_max=None):
        query = "SELECT * FROM produtos WHERE 1=1"
        params = []
        if termo:
            query += " AND (nome LIKE ? OR descricao LIKE ?)"
            like = f"%{termo}%"
            params.extend([like, like])
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            query += " AND preco <= ?"
            params.append(preco_max)

        conn = get_connection()
        try:
            rows = conn.execute(query, params).fetchall()
            return [cls._to_dict(row) for row in rows]
        finally:
            conn.close()

    @classmethod
    def count(cls):
        conn = get_connection()
        try:
            return conn.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
        finally:
            conn.close()
