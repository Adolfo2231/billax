from .base import Config


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    
    # Development specific settings
    FLASK_ENV = 'development'
    
    # Database (SQLite for development)
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///billax_dev.db'
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    @staticmethod
    def init_app(app):
        """Initialize application with development configuration."""
        Config.init_app(app)
        
        # Development specific initializations can go here
        print("Running in development mode") 