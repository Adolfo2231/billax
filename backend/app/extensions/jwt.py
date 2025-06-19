"""
JWT extension configuration and utilities.

This module configures JWT authentication using flask_jwt_extended.
It provides token generation, verification, and user loading functionality.
"""

from flask_jwt_extended import JWTManager, create_access_token
from datetime import timedelta
from typing import Dict, Any

# Initialize JWT manager
jwt = JWTManager()

def configure_jwt(jwt_manager):
    """Configure JWT manager with error handlers and utilities.
    
    Args:
        jwt_manager: JWTManager instance to configure
    """
    # Register error handlers
    @jwt_manager.invalid_token_loader
    def invalid_token_callback(error):
        return {
            'error': 'invalid_token',
            'message': 'Token signature verification failed'
        }, 401
        
    @jwt_manager.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return {
            'error': 'token_expired',
            'message': 'Token has expired'
        }, 401
        
    @jwt_manager.unauthorized_loader
    def unauthorized_callback(error):
        return {
            'error': 'authorization_required',
            'message': 'Authorization header is missing'
        }, 401

def init_jwt(app):
    """Initialize JWT with the application.
    
    Args:
        app: Flask application instance
    """
    # Configure JWT settings
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    
    # Initialize and configure JWT
    jwt.init_app(app)
    configure_jwt(jwt)

def create_token(user_id: int) -> str:
    """Create an access token for a user.
    
    Args:
        user_id: The ID of the user to create a token for
        
    Returns:
        str: The generated JWT access token
    """
    return create_access_token(
        identity=user_id,
        additional_claims={'type': 'access'}
    ) 