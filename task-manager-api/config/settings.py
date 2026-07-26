"""Configuração da aplicação a partir de variáveis de ambiente.

Nenhuma credencial deve ser hardcoded aqui. Os valores são lidos de
variáveis de ambiente (carregadas de um arquivo .env em desenvolvimento),
com fallbacks seguros apenas para uso local.
"""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Segurança / Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-prod')

    # Banco de dados (mantém SQLite/SQLAlchemy do projeto original)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

    # SMTP (usado pelo NotificationService)
    SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USER = os.environ.get('SMTP_USER', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


def get_config():
    """Seleciona a classe de configuração conforme FLASK_ENV."""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    if env == 'production':
        return ProductionConfig
    return DevelopmentConfig
