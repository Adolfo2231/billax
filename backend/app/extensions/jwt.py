"""
JWT extension configuration and utilities.

This module configures JWT authentication using flask_jwt_extended.
It provides token generation, verification, and user loading functionality.
"""

from flask_jwt_extended import JWTManager, create_access_token
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.models.blacklisted_token import BlacklistedToken
from app.extensions import db

# Initialize JWT manager globally (used in extensions.py)
jwt = JWTManager()

def configure_jwt(jwt_manager: JWTManager) -> None:
    """Configure JWT manager with error handlers and token validation hooks."""

    @jwt_manager.invalid_token_loader
    def invalid_token_callback(error: str):
        return {
            'error': 'invalid_token',
            'message': 'Token signature verification failed'
        }, 401

    @jwt_manager.expired_token_loader
    def expired_token_callback(jwt_header: Dict[str, Any], jwt_data: Dict[str, Any]):
        return {
            'error': 'token_expired',
            'message': 'Token has expired'
        }, 401

    @jwt_manager.unauthorized_loader
    def unauthorized_callback(error: str):
        return {
            'error': 'authorization_required',
            'message': 'Authorization header is missing'
        }, 401

    @jwt_manager.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header: Dict[str, Any], jwt_payload: Dict[str, Any]) -> bool:
        """Check if the token's jti is blacklisted."""
        jti = jwt_payload.get("jti")  # CAMBIO: más seguro con .get()
        if not jti:
            return True  # Deniega por seguridad si no hay jti
        return is_token_blacklisted(jti)


def init_jwt(app) -> None:
    """Initialize JWT extension and bind it to the app."""
    
    # CAMBIO: Usa valor propio de configuración, con fallback seguro
    app.config.setdefault('JWT_SECRET_KEY', app.config.get('SECRET_KEY', 'change-me'))
    app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', timedelta(days=1))
    app.config.setdefault('JWT_BLOCKLIST_ENABLED', True)
    app.config.setdefault('JWT_BLOCKLIST_TOKEN_CHECKS', ['access'])

    jwt.init_app(app)
    configure_jwt(jwt)


def create_token(user_id: int) -> str:
    """Create a new JWT access token for a user."""
    return create_access_token(
        identity=str(user_id),
        additional_claims={'type': 'access'}
    )


def is_token_blacklisted(jti: str) -> bool:
    """Check if a token is present in the blacklist."""
    if not jti:
        return True  # CAMBIO: protección extra

    token: Optional[BlacklistedToken] = BlacklistedToken.query.filter_by(jti=jti).first()
    return token is not None


def blacklist_token(jti: str, user_id: int, expires_at: datetime) -> None:
    """Insert a token into the blacklist."""
    token = BlacklistedToken(
        jti=jti,
        user_id=user_id,
        expires_at=expires_at
    )
    db.session.add(token)
    db.session.commit()


def cleanup_expired_tokens() -> int:
    """Remove tokens from the blacklist that have already expired."""
    now = datetime.utcnow()
    expired_tokens = BlacklistedToken.query.filter(
        BlacklistedToken.expires_at < now
    ).all()

    count = len(expired_tokens)
    for token in expired_tokens:
        db.session.delete(token)

    db.session.commit()
    return count
