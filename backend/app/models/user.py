"""
models/user.py

This module defines the User model for the Billax finance application.
It includes basic field validation and secure password handling.

The User model represents a registered user in the system and handles:
- User registration and authentication
- Secure password storage
- Basic data validation for name, email, and password
"""

import re
from datetime import datetime
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """
    Represents a registered user in the Billax finance application.

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, email: str, password: str, first_name: str, last_name: str, role: str = 'user'):
        """
        Initialize a new User instance.

        Args:
            email (str): User's email address.
            password (str): Plain text password (will be hashed).
            first_name (str): User's first name.
            last_name (str): User's last name.
            role (str): User's role. Defaults to 'user'.
        """
        # Validate email
        self.validate_email(email)
        self.email = email
        
        # Validate and hash password
        self.set_password(password)
        
        # Validate names
        self.validate_name(first_name, "First name")
        self.first_name = first_name
        
        self.validate_name(last_name, "Last name")
        self.last_name = last_name
        
        # Set role (no validation needed as it has a default)
        self.role = role

    def __repr__(self):
        """Returns a string representation of the user."""
        return f'<User {self.email}>'

    @property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    def set_password(self, password: str):
        """Hash and set the password."""
        if not isinstance(password, str):
            raise ValueError("Password must be a string")
        
        if not password:
            raise ValueError("Password is required")
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_email(email):
        """Validate email format."""
        if not isinstance(email, str):
            raise ValueError("Email must be a string")
        
        if not email:
            raise ValueError("Email is required")
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")

    @staticmethod
    def validate_name(name, field_name="Name"):
        """Validate first name or last name."""
        if not isinstance(name, str):
            raise ValueError(f"{field_name} must be a string")
        
        if not name:
            raise ValueError(f"{field_name} is required")
        
        if len(name.strip()) < 2:
            raise ValueError(f"{field_name} must be at least 2 characters long")
        
        if len(name.strip()) > 50:
            raise ValueError(f"{field_name} must be less than 50 characters")

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