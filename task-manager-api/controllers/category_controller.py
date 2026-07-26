"""Lógica de negócio de categorias (independente de HTTP)."""
import logging

from constants import DEFAULT_COLOR
from database import db
from exceptions import AppException, NotFoundError, ValidationError
from models.category import Category
from models.task import Task

logger = logging.getLogger(__name__)


class CategoryController:
    def list_categories(self):
        categories = Category.query.all()
        counts = dict(
            db.session.query(Task.category_id, db.func.count(Task.id))
            .group_by(Task.category_id)
            .all()
        )
        result = []
        for category in categories:
            data = category.to_dict()
            data['task_count'] = counts.get(category.id, 0)
            result.append(data)
        return result

    def create_category(self, data):
        if not data:
            raise ValidationError('Dados inválidos')

        name = data.get('name')
        if not name:
            raise ValidationError('Nome é obrigatório')

        category = Category()
        category.name = name
        category.description = data.get('description', '')
        category.color = data.get('color', DEFAULT_COLOR)

        try:
            db.session.add(category)
            db.session.commit()
            return category.to_dict()
        except Exception as exc:
            db.session.rollback()
            logger.error('Erro ao criar categoria: %s', exc)
            raise AppException('Erro ao criar categoria', 500)

    def update_category(self, category_id, data):
        category = self._get_or_404(category_id)
        if not data:
            raise ValidationError('Dados inválidos')

        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'color' in data:
            category.color = data['color']

        try:
            db.session.commit()
            return category.to_dict()
        except Exception as exc:
            db.session.rollback()
            logger.error('Erro ao atualizar categoria: %s', exc)
            raise AppException('Erro ao atualizar', 500)

    def delete_category(self, category_id):
        category = self._get_or_404(category_id)
        try:
            db.session.delete(category)
            db.session.commit()
            return {'message': 'Categoria deletada'}
        except Exception as exc:
            db.session.rollback()
            logger.error('Erro ao deletar categoria: %s', exc)
            raise AppException('Erro ao deletar', 500)

    def _get_or_404(self, category_id):
        category = Category.query.get(category_id)
        if not category:
            raise NotFoundError('Categoria não encontrada')
        return category
