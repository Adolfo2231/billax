import os
from flask import Flask
from .config import DevelopmentConfig, ProductionConfig
from app.extensions import db, migrate, jwt, mail, cors


def create_app(config_class=None):
    # Auto-detect configuration based on environment
    if config_class is None:
        if os.environ.get('FLASK_ENV') == 'production':
            config_class = ProductionConfig
        else:
            config_class = DevelopmentConfig
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    # Initialize extensions (only if database is available)
    if app.config.get('SQLALCHEMY_DATABASE_URI') and not app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite:///'):
        db.init_app(app)
        migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    # Initialize CORS with proper origins
    from .extensions.cors import init_cors
    init_cors(app)
    
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
    
    @app.route('/ready')
    def ready():
        """Readiness check endpoint for Railway."""
        return {'status': 'ready', 'service': 'billax'}, 200
    
    @app.route('/cors-test')
    def cors_test():
        """Test endpoint to verify CORS is working."""
        return {
            'status': 'success',
            'message': 'CORS is working correctly',
            'service': 'billax',
            'timestamp': '2025-07-20T18:30:00Z'
        }, 200
    
    return app 