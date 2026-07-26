from routes.order_routes import order_bp
from routes.product_routes import product_bp
from routes.system_routes import system_bp
from routes.user_routes import user_bp


def register_routes(app):
    app.register_blueprint(product_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(system_bp)
