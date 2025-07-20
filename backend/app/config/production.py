import os
from .base import Config


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    
    # Production specific settings
    FLASK_ENV = 'production'
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database (PostgreSQL for production)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Logging
    LOG_LEVEL = 'WARNING'
    
    @staticmethod
    def init_app(app):
        """Initialize application with production configuration."""
        Config.init_app(app)
        
        # Production specific initializations can go here
        # Example: Sentry integration, etc. 