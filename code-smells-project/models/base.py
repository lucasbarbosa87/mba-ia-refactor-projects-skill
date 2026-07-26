import sqlite3

from werkzeug.security import generate_password_hash

from config.settings import Config
from utils.constants import UserRole

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        descricao TEXT,
        preco REAL,
        estoque INTEGER,
        categoria TEXT,
        ativo INTEGER DEFAULT 1,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT,
        senha TEXT,
        tipo TEXT DEFAULT 'cliente',
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        status TEXT DEFAULT 'pendente',
        total REAL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER,
        preco_unitario REAL
    )
    """,
]

SEED_PRODUTOS = [
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
]

# Senhas de exemplo em texto plano; são convertidas para hash antes de gravar.
SEED_USUARIOS = [
    ("Admin", "admin@loja.com", "admin123", UserRole.ADMIN.value),
    ("João Silva", "joao@email.com", "123456", UserRole.CLIENTE.value),
    ("Maria Santos", "maria@email.com", "senha123", UserRole.CLIENTE.value),
]


def get_connection():
    """Abre uma nova conexão por chamada (fechada pelo chamador)."""
    conn = sqlite3.connect(Config.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria o schema e popula dados de exemplo no primeiro boot."""
    conn = get_connection()
    try:
        for statement in SCHEMA:
            conn.execute(statement)
        conn.commit()

        if conn.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
                "VALUES (?, ?, ?, ?, ?)",
                SEED_PRODUTOS,
            )
            usuarios = [
                (nome, email, generate_password_hash(senha), tipo)
                for nome, email, senha, tipo in SEED_USUARIOS
            ]
            conn.executemany(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                usuarios,
            )
            conn.commit()
    finally:
        conn.close()


def reset_all():
    """Limpa todas as tabelas (uso administrativo)."""
    conn = get_connection()
    try:
        for table in ("itens_pedido", "pedidos", "produtos", "usuarios"):
            conn.execute(f"DELETE FROM {table}")
        conn.commit()
    finally:
        conn.close()


def execute_raw(sql):
    """Executa SQL arbitrário (uso administrativo, atrás de autenticação).

    Retorna (linhas, is_select)."""
    conn = get_connection()
    try:
        cursor = conn.execute(sql)
        if sql.strip().upper().startswith("SELECT"):
            return [dict(row) for row in cursor.fetchall()], True
        conn.commit()
        return None, False
    finally:
        conn.close()
