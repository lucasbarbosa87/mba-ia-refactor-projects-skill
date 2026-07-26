"""Funções utilitárias reutilizáveis (sem dependência de camadas superiores)."""
import re
from datetime import datetime, timezone

from constants import DATE_FORMAT


def now_utc():
    """Retorna o horário UTC atual como datetime *naive*.

    Substitui datetime.utcnow() (deprecado no Python 3.12+) mantendo o
    comportamento naive esperado pelas comparações com due_date.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_date(date_obj):
    if date_obj:
        return str(date_obj)
    return None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return bool(re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email))


def parse_iso_date(date_string):
    """Faz o parse de uma data no formato YYYY-MM-DD, ou None se inválida."""
    try:
        return datetime.strptime(date_string, DATE_FORMAT)
    except (ValueError, TypeError):
        return None
