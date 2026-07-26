from flask import Blueprint, jsonify

from controllers.report_controller import ReportController

report_bp = Blueprint('reports', __name__)
controller = ReportController()


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    return jsonify(controller.summary()), 200


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    return jsonify(controller.user_report(user_id)), 200
