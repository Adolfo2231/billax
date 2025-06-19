"""
models/blacklisted_token.py

This module defines the BlacklistedToken model for storing invalidated JWT tokens.
It provides a way to track and invalidate tokens that have been logged out.
"""

from datetime import datetime
from app.extensions import db


class BlacklistedToken(db.Model):
    """
    Represents a blacklisted JWT token in the system.

    Attributes:
        id (int): Unique integer primary key.
        jti (str): JWT ID (unique identifier for the token).
        user_id (int): ID of the user who owned the token.
        expires_at (datetime): When the token would have expired.
        blacklisted_at (datetime): When the token was blacklisted.
    """

    __tablename__ = 'blacklisted_tokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    blacklisted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """Returns a string representation of the blacklisted token."""
        return f'<BlacklistedToken {self.jti}>'

    def to_dict(self):
        """Convert blacklisted token to dictionary."""
        return {
            'id': self.id,
            'jti': self.jti,
            'user_id': self.user_id,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'blacklisted_at': self.blacklisted_at.isoformat() if self.blacklisted_at else None
        } 