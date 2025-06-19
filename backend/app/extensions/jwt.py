"""
JWT extension configuration and utilities.

This module configures JWT authentication using flask_jwt_extended.
It provides token generation, verification, and user loading functionality.
"""

from flask_jwt_extended import JWTManager, create_access_token
from datetime import datetime, timedelta
from typing import Dict, Any
from app.models.blacklisted_token import BlacklistedToken
from app.extensions import db

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

    @jwt_manager.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        """Check if a token is in the blacklist."""
        jti = jwt_payload["jti"]
        return is_token_blacklisted(jti)

def init_jwt(app):
    """Initialize JWT with the application.
    
    Args:
        app: Flask application instance
    """
    # Configure JWT settings
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    app.config['JWT_BLOCKLIST_ENABLED'] = True
    app.config['JWT_BLOCKLIST_TOKEN_CHECKS'] = ['access']
    
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
        identity=str(user_id),
        additional_claims={'type': 'access'}
    )

def is_token_blacklisted(jti: str) -> bool:
    """Check if a token is in the blacklist.
    
    Args:
        jti: JWT ID to check
        
    Returns:
        bool: True if token is blacklisted, False otherwise
    """
    token = BlacklistedToken.query.filter_by(jti=jti).first()
    return token is not None

def blacklist_token(jti: str, user_id: int, expires_at: datetime) -> None:
    """Add a token to the blacklist.
    
    Args:
        jti: JWT ID of the token to blacklist
        user_id: ID of the user who owned the token
        expires_at: When the token expires
    """
    blacklisted_token = BlacklistedToken(
        jti=jti,
        user_id=user_id,
        expires_at=expires_at
    )
    db.session.add(blacklisted_token)
    db.session.commit()

def cleanup_expired_tokens() -> int:
    """Remove expired tokens from the blacklist.
    
    Returns:
        int: Number of tokens removed
    """
    now = datetime.utcnow()
    expired_tokens = BlacklistedToken.query.filter(
        BlacklistedToken.expires_at < now
    ).all()
    
    count = len(expired_tokens)
    for token in expired_tokens:
        db.session.delete(token)
    
    db.session.commit()
    return count 