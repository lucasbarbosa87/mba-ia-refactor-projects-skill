import os


class Config:
    """Configuração central da aplicação, carregada de variáveis de ambiente."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")

    # Token exigido nos endpoints administrativos. Sem valor => admin desabilitado.
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")

    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

    VERSAO = "1.0.0"
    AMBIENTE = os.environ.get("AMBIENTE", "development")
