from flask import Blueprint, jsonify, request

from controllers.task_controller import TaskController

task_bp = Blueprint('tasks', __name__)
controller = TaskController()


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(controller.list_tasks()), 200


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    result = controller.search_tasks(
        query=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=request.args.get('priority', ''),
        user_id=request.args.get('user_id', ''),
    )
    return jsonify(result), 200


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return jsonify(controller.get_stats()), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    return jsonify(controller.get_task(task_id)), 200


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    return jsonify(controller.create_task(request.get_json())), 201


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    return jsonify(controller.update_task(task_id, request.get_json())), 200


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    return jsonify(controller.delete_task(task_id)), 200
