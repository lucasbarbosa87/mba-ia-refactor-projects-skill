"""Lógica de negócio de usuários e autenticação (independente de HTTP)."""
import logging

from sqlalchemy.orm import joinedload

from constants import MIN_PASSWORD_LENGTH, UserRole
from database import db
from exceptions import (
    AppException,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from middlewares.auth import generate_token
from models.task import Task
from models.user import User
from utils.helpers import validate_email

logger = logging.getLogger(__name__)


class UserController:
    def list_users(self):
        users = User.query.options(joinedload(User.tasks)).all()
        return [
            {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'active': user.active,
                'created_at': str(user.created_at),
                'task_count': len(user.tasks),
            }
            for user in users
        ]

    def get_user(self, user_id):
        user = self._get_or_404(user_id)
        data = user.to_dict()
        tasks = Task.query.filter_by(user_id=user_id).all()
        data['tasks'] = [t.to_dict() for t in tasks]
        return data

    def get_user_tasks(self, user_id):
        self._get_or_404(user_id)
        tasks = Task.query.filter_by(user_id=user_id).all()
        result = []
        for task in tasks:
            result.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'created_at': str(task.created_at),
                'due_date': str(task.due_date) if task.due_date else None,
                'overdue': task.is_overdue(),
            })
        return result

    def create_user(self, data):
        if not data:
            raise ValidationError('Dados inválidos')

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', UserRole.USER.value)

        if not name:
            raise ValidationError('Nome é obrigatório')
        if not email:
            raise ValidationError('Email é obrigatório')
        if not password:
            raise ValidationError('Senha é obrigatória')

        if not validate_email(email):
            raise ValidationError('Email inválido')

        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValidationError('Senha deve ter no mínimo 4 caracteres')

        if User.query.filter_by(email=email).first():
            raise ConflictError('Email já cadastrado')

        if role not in UserRole.values():
            raise ValidationError('Role inválido')

        user = User()
        user.name = name
        user.email = email
        user.set_password(password)
        user.role = role

        try:
            db.session.add(user)
            db.session.commit()
            logger.info('Usuário criado: %s - %s', user.id, user.name)
            return user.to_dict()
        except Exception as exc:
            db.session.rollback()
            logger.error('Erro ao criar usuário: %s', exc)
            raise AppException('Erro ao criar usuário', 500)

    def update_user(self, user_id, data):
        user = self._get_or_404(user_id)
        if not data:
            raise ValidationError('Dados inválidos')

        if 'name' in data:
            user.name = data['name']

        if 'email' in data:
            if not validate_email(data['email']):
                raise ValidationError('Email inválido')
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                raise ConflictError('Email já cadastrado')
            user.email = data['email']

        if 'password' in data:
            if len(data['password']) < MIN_PASSWORD_LENGTH:
                raise ValidationError('Senha muito curta')
            user.set_password(data['password'])

        if 'role' in data:
            if data['role'] not in UserRole.values():
                raise ValidationError('Role inválido')
            user.role = data['role']

        if 'active' in data:
            user.active = data['active']

        try:
            db.session.commit()
            return user.to_dict()
        except Exception as exc:
            db.session.rollback()
            logger.error('Erro ao atualizar usuário: %s', exc)
            raise AppException('Erro ao atualizar', 500)

    def delete_user(self, user_id):
        user = self._get_or_404(user_id)
        tasks = Task.query.filter_by(user_id=user_id).all()
        for task in tasks:
            db.session.delete(task)
        try:
            db.session.delete(user)
            db.session.commit()
            logger.info('Usuário deletado: %s', user_id)
            return {'message': 'Usuário deletado com sucesso'}
        except Exception as exc:
            db.session.rollback()
            logger.error('Erro ao deletar usuário: %s', exc)
            raise AppException('Erro ao deletar', 500)

    def authenticate(self, data):
        if not data:
            raise ValidationError('Dados inválidos')

        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            raise ValidationError('Email e senha são obrigatórios')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise UnauthorizedError('Credenciais inválidas')

        if not user.active:
            raise ForbiddenError('Usuário inativo')

        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': generate_token(user.id),
        }

    def _get_or_404(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')
        return user
