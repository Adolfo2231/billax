"""
models/user.py

This module defines the User model for the Billax financial application.
It includes basic field validation and secure password handling.

The User model represents a registered user in the system and handles:
- User registration and authentication
- Secure password storage
- Basic field validation using SQLAlchemy validators
"""

import re
from datetime import datetime
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates


class User(db.Model):
    """
    Represents a registered user in the Billax financial application.

    Attributes:
        id (int): Unique integer primary key.
        email (str): Unique email address of the user.
        password_hash (str): Securely hashed password.
        first_name (str): User's first name.
        last_name (str): User's last name.
        role (str): Role of the user (user, admin, moderator).
        created_at (datetime): When the user was created.
        updated_at (datetime): When the user was last updated.
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    plaid_access_token = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    goals = db.relationship('Goal', back_populates='user', cascade='all, delete-orphan')

    @validates('email')
    def validate_email(self, key, email):
        """Validate email format."""
        if not email:
            raise ValueError("Email is required")
        
        if not isinstance(email, str):
            raise ValueError("Email must be a string")
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        
        return email

    @validates('first_name')
    def validate_first_name(self, key, first_name):
        """Validate first name format."""
        if not first_name:
            raise ValueError("First name is required")
        
        if not isinstance(first_name, str):
            raise ValueError("First name must be a string")
        
        if len(first_name.strip()) < 2:
            raise ValueError("First name must be at least 2 characters long")
        
        if len(first_name.strip()) > 50:
            raise ValueError("First name must be less than 50 characters")
        
        return first_name.strip()

    @validates('last_name')
    def validate_last_name(self, key, last_name):
        """Validate last name format."""
        if not last_name:
            raise ValueError("Last name is required")
        
        if not isinstance(last_name, str):
            raise ValueError("Last name must be a string")
        
        if len(last_name.strip()) < 2:
            raise ValueError("Last name must be at least 2 characters long")
        
        if len(last_name.strip()) > 50:
            raise ValueError("Last name must be less than 50 characters")
        
        return last_name.strip()

    def __repr__(self):
        """Returns a string representation of the user."""
        return f'<User {self.email}>'

    @property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, password: str):
        if not password:
            raise ValueError("Password is required")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'

    def __init__(self, *args, password=None, **kwargs):
        super().__init__(*args, **kwargs)
        if password is not None:
            self.password = password  # Esto usa el property y hace hash/validación 