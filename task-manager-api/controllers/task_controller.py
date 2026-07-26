"""Lógica de negócio de tasks (independente de HTTP)."""
import logging
from datetime import datetime

from sqlalchemy.orm import joinedload

from constants import (
    DATE_FORMAT,
    DEFAULT_PRIORITY,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    TaskStatus,
)
from database import db
from exceptions import AppException, NotFoundError, ValidationError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import calculate_percentage

logger = logging.getLogger(__name__)


class TaskController:
    # ---- Leitura -------------------------------------------------------
    def list_tasks(self):
        tasks = (
            Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
        )
        return [self._serialize_full(t) for t in tasks]

    def get_task(self, task_id):
        task = self._get_or_404(task_id)
        data = task.to_dict()
        data['overdue'] = task.is_overdue()
        return data

    def search_tasks(self, query='', status='', priority='', user_id=''):
        tasks = Task.query
        if query:
            tasks = tasks.filter(
                db.or_(
                    Task.title.like(f'%{query}%'),
                    Task.description.like(f'%{query}%'),
                )
            )
        if status:
            tasks = tasks.filter(Task.status == status)
        if priority:
            tasks = tasks.filter(Task.priority == self._to_int(priority, 'Prioridade inválida'))
        if user_id:
            tasks = tasks.filter(Task.user_id == self._to_int(user_id, 'user_id inválido'))

        return [t.to_dict() for t in tasks.all()]

    def get_stats(self):
        tasks = Task.query.all()
        total = len(tasks)
        counts = {status: 0 for status in TaskStatus.values()}
        overdue = 0
        for task in tasks:
            if task.status in counts:
                counts[task.status] += 1
            if task.is_overdue():
                overdue += 1
        done = counts[TaskStatus.DONE.value]
        return {
            'total': total,
            'pending': counts[TaskStatus.PENDING.value],
            'in_progress': counts[TaskStatus.IN_PROGRESS.value],
            'done': done,
            'cancelled': counts[TaskStatus.CANCELLED.value],
            'overdue': overdue,
            'completion_rate': calculate_percentage(done, total),
        }

    # ---- Escrita -------------------------------------------------------
    def create_task(self, data):
        if not data:
            raise ValidationError('Dados inválidos')

        title = data.get('title')
        if not title:
            raise ValidationError('Título é obrigatório')
        self._validate_title_length(title)

        status = data.get('status', TaskStatus.PENDING.value)
        if status not in TaskStatus.values():
            raise ValidationError('Status inválido')

        priority = data.get('priority', DEFAULT_PRIORITY)
        if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
            raise ValidationError('Prioridade deve ser entre 1 e 5')

        user_id = data.get('user_id')
        if user_id:
            self._ensure_user_exists(user_id)

        category_id = data.get('category_id')
        if category_id:
            self._ensure_category_exists(category_id)

        task = Task()
        task.title = title
        task.description = data.get('description', '')
        task.status = status
        task.priority = priority
        task.user_id = user_id
        task.category_id = category_id

        due_date = data.get('due_date')
        if due_date:
            task.due_date = self._parse_due_date(
                due_date, 'Formato de data inválido. Use YYYY-MM-DD'
            )

        self._apply_tags(task, data.get('tags'))

        try:
            db.session.add(task)
            db.session.commit()
            logger.info('Task criada: %s - %s', task.id, task.title)
            return task.to_dict()
        except Exception as exc:
            db.session.rollback()
            logger.error('Erro ao criar task: %s', exc)
            raise AppException('Erro ao criar task', 500)

    def update_task(self, task_id, data):
        task = self._get_or_404(task_id)
        if not data:
            raise ValidationError('Dados inválidos')

        if 'title' in data:
            self._validate_title_length(data['title'])
            task.title = data['title']

        if 'description' in data:
            task.description = data['description']

        if 'status' in data:
            if data['status'] not in TaskStatus.values():
                raise ValidationError('Status inválido')
            task.status = data['status']

        if 'priority' in data:
            if data['priority'] < MIN_PRIORITY or data['priority'] > MAX_PRIORITY:
                raise ValidationError('Prioridade deve ser entre 1 e 5')
            task.priority = data['priority']

        if 'user_id' in data:
            if data['user_id']:
                self._ensure_user_exists(data['user_id'])
            task.user_id = data['user_id']

        if 'category_id' in data:
            if data['category_id']:
                self._ensure_category_exists(data['category_id'])
            task.category_id = data['category_id']

        if 'due_date' in data:
            if data['due_date']:
                task.due_date = self._parse_due_date(
                    data['due_date'], 'Formato de data inválido'
                )
            else:
                task.due_date = None

        if 'tags' in data:
            self._apply_tags(task, data['tags'])

        try:
            db.session.commit()
            logger.info('Task atualizada: %s', task.id)
            return task.to_dict()
        except Exception as exc:
            db.session.rollback()
            logger.error('Erro ao atualizar task: %s', exc)
            raise AppException('Erro ao atualizar', 500)

    def delete_task(self, task_id):
        task = self._get_or_404(task_id)
        try:
            db.session.delete(task)
            db.session.commit()
            logger.info('Task deletada: %s', task_id)
            return {'message': 'Task deletada com sucesso'}
        except Exception as exc:
            db.session.rollback()
            logger.error('Erro ao deletar task: %s', exc)
            raise AppException('Erro ao deletar', 500)

    # ---- Helpers internos ---------------------------------------------
    def _serialize_full(self, task):
        data = task.to_dict()
        data['overdue'] = task.is_overdue()
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
        return data

    def _get_or_404(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            raise NotFoundError('Task não encontrada')
        return task

    def _validate_title_length(self, title):
        if len(title) < MIN_TITLE_LENGTH:
            raise ValidationError('Título muito curto')
        if len(title) > MAX_TITLE_LENGTH:
            raise ValidationError('Título muito longo')

    def _ensure_user_exists(self, user_id):
        if not User.query.get(user_id):
            raise NotFoundError('Usuário não encontrado')

    def _ensure_category_exists(self, category_id):
        if not Category.query.get(category_id):
            raise NotFoundError('Categoria não encontrada')

    def _parse_due_date(self, value, error_message):
        try:
            return datetime.strptime(value, DATE_FORMAT)
        except (ValueError, TypeError):
            raise ValidationError(error_message)

    def _apply_tags(self, task, tags):
        if tags is None:
            return
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    def _to_int(self, value, error_message):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValidationError(error_message)
