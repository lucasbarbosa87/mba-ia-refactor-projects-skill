"""Geração de relatórios e estatísticas (independente de HTTP)."""
from collections import defaultdict
from datetime import timedelta

from constants import TaskStatus
from exceptions import NotFoundError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import calculate_percentage, now_utc


class ReportController:
    def summary(self):
        now = now_utc()
        seven_days_ago = now - timedelta(days=7)

        tasks = Task.query.all()
        users = User.query.all()

        status_counts = defaultdict(int)
        priority_counts = defaultdict(int)
        overdue_list = []
        recent_created = 0
        recent_done = 0
        tasks_by_user = defaultdict(list)

        for task in tasks:
            status_counts[task.status] += 1
            priority_counts[task.priority] += 1
            tasks_by_user[task.user_id].append(task)

            if task.is_overdue():
                overdue_list.append({
                    'id': task.id,
                    'title': task.title,
                    'due_date': str(task.due_date),
                    'days_overdue': (now - task.due_date).days,
                })

            if task.created_at and task.created_at >= seven_days_ago:
                recent_created += 1
            if (
                task.status == TaskStatus.DONE.value
                and task.updated_at
                and task.updated_at >= seven_days_ago
            ):
                recent_done += 1

        user_stats = []
        for user in users:
            user_tasks = tasks_by_user.get(user.id, [])
            total = len(user_tasks)
            completed = sum(1 for t in user_tasks if t.status == TaskStatus.DONE.value)
            user_stats.append({
                'user_id': user.id,
                'user_name': user.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': calculate_percentage(completed, total),
            })

        return {
            'generated_at': str(now),
            'overview': {
                'total_tasks': len(tasks),
                'total_users': len(users),
                'total_categories': Category.query.count(),
            },
            'tasks_by_status': {
                'pending': status_counts[TaskStatus.PENDING.value],
                'in_progress': status_counts[TaskStatus.IN_PROGRESS.value],
                'done': status_counts[TaskStatus.DONE.value],
                'cancelled': status_counts[TaskStatus.CANCELLED.value],
            },
            'tasks_by_priority': {
                'critical': priority_counts[1],
                'high': priority_counts[2],
                'medium': priority_counts[3],
                'low': priority_counts[4],
                'minimal': priority_counts[5],
            },
            'overdue': {
                'count': len(overdue_list),
                'tasks': overdue_list,
            },
            'recent_activity': {
                'tasks_created_last_7_days': recent_created,
                'tasks_completed_last_7_days': recent_done,
            },
            'user_productivity': user_stats,
        }

    def user_report(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')

        tasks = Task.query.filter_by(user_id=user_id).all()
        total = len(tasks)
        counts = defaultdict(int)
        overdue = 0
        high_priority = 0

        for task in tasks:
            counts[task.status] += 1
            if task.priority <= 2:
                high_priority += 1
            if task.is_overdue():
                overdue += 1

        done = counts[TaskStatus.DONE.value]
        return {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
            },
            'statistics': {
                'total_tasks': total,
                'done': done,
                'pending': counts[TaskStatus.PENDING.value],
                'in_progress': counts[TaskStatus.IN_PROGRESS.value],
                'cancelled': counts[TaskStatus.CANCELLED.value],
                'overdue': overdue,
                'high_priority': high_priority,
                'completion_rate': calculate_percentage(done, total),
            },
        }
