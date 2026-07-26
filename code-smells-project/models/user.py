from werkzeug.security import check_password_hash, generate_password_hash

from models.base import get_connection
from utils.constants import UserRole


class User:
    @staticmethod
    def _to_dict(row):
        """Serialização pública — nunca inclui a senha/hash."""
        if row is None:
            return None
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
            "criado_em": row["criado_em"],
        }

    @classmethod
    def all(cls):
        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM usuarios").fetchall()
            return [cls._to_dict(row) for row in rows]
        finally:
            conn.close()

    @classmethod
    def find_by_id(cls, usuario_id):
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM usuarios WHERE id = ?", [usuario_id]
            ).fetchone()
            return cls._to_dict(row)
        finally:
            conn.close()

    @classmethod
    def find_by_email(cls, email):
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM usuarios WHERE email = ?", [email]
            ).fetchone()
        finally:
            conn.close()

    @classmethod
    def create(cls, nome, email, senha, tipo=UserRole.CLIENTE.value):
        conn = get_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                [nome, email, generate_password_hash(senha), tipo],
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @classmethod
    def verify_login(cls, email, senha):
        """Retorna o dict público do usuário se as credenciais forem válidas."""
        row = cls.find_by_email(email)
        if row and check_password_hash(row["senha"], senha):
            return cls._to_dict(row)
        return None

    @classmethod
    def count(cls):
        conn = get_connection()
        try:
            return conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        finally:
            conn.close()
