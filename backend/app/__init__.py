from flask import Flask
from .config import DevelopmentConfig
from app.extensions import db, migrate, jwt, mail


def create_app(config_class=DevelopmentConfig):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    
    
    # Register routes
    from .api.v1 import api_v1_bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Basic route for testing
    @app.route('/')
    def index():
        return {'message': 'Billax API is running!'}
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'billax'}
    
    return app 