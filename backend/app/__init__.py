import os
from flask import Flask
from .config import DevelopmentConfig, ProductionConfig
from app.extensions import db, migrate, jwt, mail, cors


def create_app(config_class=None):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Auto-detect configuration based on environment
    if config_class is None:
        if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('DATABASE_URL'):
            config_class = ProductionConfig
        else:
            config_class = DevelopmentConfig
    
    # Load configuration
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Configure CORS based on environment
    if config_class == ProductionConfig:
        cors.init_app(app, resources={
            r"/api/*": {"origins": [app.config.get('FRONTEND_URL')]}
        })
    else:
        cors.init_app(app, resources={
            r"/api/*": {"origins": "*"}
        })
    
    # Register routes
    from .api.v1 import api_v1_bp as api_bp
    app.register_blueprint(api_bp)
    
    # Basic route for testing
    @app.route('/')
    def index():
        return {'message': 'Billax API is running!'}
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'billax'}
    
    return app 