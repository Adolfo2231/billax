import os
from .base import Config


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    
    # Production specific settings
    FLASK_ENV = 'production'
    
    # Security - Use environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # Database (PostgreSQL for production)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # External APIs
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
    PLAID_SECRET = os.environ.get('PLAID_SECRET')
    PLAID_ENV = os.environ.get('PLAID_ENV')
    
    # Frontend URL for CORS - Use environment variable or default to Disco subdomain
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://billax.srv-13f27fc66efe43ff.ondis.co')
    
    # Logging
    LOG_LEVEL = 'WARNING'
    
    @staticmethod
    def init_app(app):
        """Initialize application with production configuration."""
        Config.init_app(app)
        
        # Production specific initializations can go here
        # Example: Sentry integration, etc. 