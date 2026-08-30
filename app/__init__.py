from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import config

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    # Configure logging
    from app.utils.logger import setup_logger
    setup_logger(app)

    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.users import users_bp
    from app.routes.events import events_bp
    from app.routes.seats import seats_bp
    from app.routes.bookings import bookings_bp
    from app.routes.payments import payments_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(events_bp, url_prefix='/api')
    app.register_blueprint(seats_bp, url_prefix='/api')
    app.register_blueprint(bookings_bp, url_prefix='/api')
    app.register_blueprint(payments_bp, url_prefix='/api')

    return app
