"""Constantes e enums de domínio, centralizando magic strings/numbers."""
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'
    CANCELLED = 'cancelled'

    @classmethod
    def values(cls):
        return [status.value for status in cls]


class UserRole(str, Enum):
    USER = 'user'
    ADMIN = 'admin'
    MANAGER = 'manager'

    @classmethod
    def values(cls):
        return [role.value for role in cls]


# Regras de validação
MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200
MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3
MIN_PASSWORD_LENGTH = 4
DEFAULT_COLOR = '#000000'
DATE_FORMAT = '%Y-%m-%d'
