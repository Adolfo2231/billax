"""
models/user.py

This module defines the User model for the finance application using Flask-SQLAlchemy.
It includes field-level validation, secure password handling, and exception-based
error handling for invalid user data.

The User model represents a registered user in the system and handles:
- User registration and authentication
- Secure password storage using PBKDF2
- Integration with Plaid for financial data access
- Data validation for name, email, and password

Example:
    >>> user = User(name="John Doe", email="john@example.com", password="secure123")
    >>> user.check_password("secure123")
    True
"""

import uuid
import re
from typing import Optional
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates
from app.exceptions.exceptions import InvalidNameError, InvalidEmailError, InvalidPasswordError


class User(db.Model):
    """
    Represents a registered user in the finance application.

    This model handles user authentication and financial data access through Plaid.
    It includes secure password storage and validation for user data.

    Attributes:
        id (str): Unique UUID used as the primary key.
        name (str): Full name of the user.
        email (str): Unique email address of the user.
        password_hash (str): Securely hashed password using PBKDF2.
        plaid_access_token (Optional[str]): Token for accessing Plaid API, if connected.

    Example:
        >>> user = User(name="John Doe", email="john@example.com", password="secure123")
        >>> user.check_password("secure123")
        True
    """

    __tablename__: str = 'users'

    id: str = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: str = db.Column(db.String(120), nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(128), nullable=False)
    plaid_access_token: Optional[str] = db.Column(db.String(200), nullable=True)

    def __init__(self, name: str, email: str, password: str) -> None:
        """
        Initialize a new User instance with validation and secure password hashing.

        Args:
            name (str): User's full name. Must be at least 2 characters and contain only letters and spaces.
            email (str): User's email address. Must be a valid email format.
            password (str): Plain-text password. Must be at least 6 characters.

        Raises:
            InvalidNameError: If the name is too short or contains invalid characters.
            InvalidEmailError: If the email format is invalid.
            InvalidPasswordError: If the password is less than 6 characters.

        Example:
            >>> user = User(name="John Doe", email="john@example.com", password="secure123")
        """
        self.name = name  # triggers @validates("name")
        self.email = email  # triggers @validates("email")
        self.set_password(password)

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        """
        Validates the user's name format.

        The name must:
        - Be at least 2 characters long
        - Contain only letters and spaces
        - Not be empty

        Args:
            key (str): The column name being validated ("name").
            value (str): The name value to validate.

        Returns:
            str: The validated name.

        Raises:
            InvalidNameError: If the name format is invalid.

        Example:
            >>> user = User(name="John Doe", email="john@example.com", password="secure123")
            >>> user.name
            'John Doe'
        """
        if not re.match(r"^[a-zA-Z\s]{2,}$", value):
            raise InvalidNameError()
        return value

    @validates("email")
    def validate_email(self, key: str, value: str) -> str:
        """
        Validates the format of the email address.

        The email must:
        - Contain exactly one @ symbol
        - Have a valid domain
        - Not be empty

        Args:
            key (str): The column name being validated ("email").
            value (str): The email address to validate.

        Returns:
            str: The validated email address.

        Raises:
            InvalidEmailError: If the email format is invalid.

        Example:
            >>> user = User(name="John Doe", email="john@example.com", password="secure123")
            >>> user.email
            'john@example.com'
        """
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise InvalidEmailError()
        return value

    def set_password(self, password: str) -> None:
        """
        Hashes and stores the password securely using PBKDF2.

        The password must:
        - Be at least 6 characters long
        - Not be empty

        Args:
            password (str): The plain-text password to hash.

        Raises:
            InvalidPasswordError: If the password is too short.

        Example:
            >>> user = User(name="John Doe", email="john@example.com", password="secure123")
            >>> user.check_password("secure123")
            True
        """
        if len(password) < 6:
            raise InvalidPasswordError("Password must be at least 6 characters long.")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Verifies that a given password matches the stored hashed password.

        Args:
            password (str): The plain-text password to verify.

        Returns:
            bool: True if the password is correct, False otherwise.

        Example:
            >>> user = User(name="John Doe", email="john@example.com", password="secure123")
            >>> user.check_password("secure123")
            True
            >>> user.check_password("wrongpassword")
            False
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        """
        Returns a human-readable representation of the user object.

        Returns:
            str: A string containing the user's name and email.

        Example:
            >>> user = User(name="John Doe", email="john@example.com", password="secure123")
            >>> repr(user)
            "<User(name='John Doe', email='john@example.com')>"
        """
        return f"<User(name='{self.name}', email='{self.email}')>"
