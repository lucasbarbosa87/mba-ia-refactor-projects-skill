import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Config
from middlewares.error_handler import register_error_handlers
from models.base import init_db
from routes import register_routes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app():
    """Composition root: monta a aplicação e registra suas dependências."""
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    init_db()
    register_routes(app)
    register_error_handlers(app)

    return app


app = create_app()


if __name__ == "__main__":
    logger.info("Servidor iniciado em http://%s:%s", Config.HOST, Config.PORT)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
