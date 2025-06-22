from .base import Config
import os
from dotenv import load_dotenv

load_dotenv()

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    
    # Development specific settings
    FLASK_ENV = 'development'
    
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    @staticmethod
    def init_app(app):
        """Initialize application with development configuration."""
        Config.init_app(app)
        
        # Development specific initializations can go here
        print("Running in development mode") 