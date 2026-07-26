"""Entry point / composition root da aplicação (application factory)."""
import logging
from datetime import datetime

from flask import Flask
from flask_cors import CORS

from config.settings import get_config
from database import db
from middlewares.error_handler import register_error_handlers
from routes import register_routes


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or get_config())

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    )

    CORS(app)
    db.init_app(app)

    register_routes(app)
    register_error_handlers(app)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(datetime.now())}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
