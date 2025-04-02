import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
mail = Mail()
migrate = Migrate()

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Create upload directories
    os.makedirs(os.path.join(app.static_folder, 'uploads', 'image'), exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'uploads', 'document'), exist_ok=True)

    # Register blueprints
    from app.routes import main
    from app.auth import auth
    from app.content import content
    from app.api import api

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(content, url_prefix='/content')
    app.register_blueprint(api, url_prefix='/api')

    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)

    # Register CLI commands
    from app.cli import register_commands
    register_commands(app)

    return app
