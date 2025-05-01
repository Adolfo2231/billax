"""
Authentication Facade for managing user authentication and authorization.

This module provides a facade class that handles business logic related to user authentication,
including registration, login, and token generation. It acts as an intermediary between the
API layer and the database, managing:
- User registration with validation
- User login and credential verification
- JWT token generation and management
- Error handling and data persistence

The facade pattern is used to provide a simplified interface to complex subsystems,
hiding implementation details and providing a clean API for the rest of the application.

Example:
    >>> from app.facade.auth_facade import AuthFacade
    >>> auth = AuthFacade()
    >>> # Register a new user
    >>> result = auth.register_user({
    ...     'name': 'John Doe',
    ...     'email': 'john@example.com',
    ...     'password': 'securepassword123'
    ... })
    >>> print(result['message'])
    User registered successfully.
"""

from typing import Dict, Any
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.helpers import generate_jwt
from app.exceptions.validation_exception import ValidationException
from app.extensions import db

class AuthFacade:
    """
    Business logic layer for handling user authentication and authorization.

    This class provides a simplified interface for managing user authentication in the system.
    It handles all business logic related to user registration, login, and token generation,
    ensuring proper validation and security measures are in place.

    Example:
        >>> auth = AuthFacade()
        >>> # Register and login a user
        >>> auth.register_user({
        ...     'name': 'John Doe',
        ...     'email': 'john@example.com',
        ...     'password': 'securepassword123'
        ... })
        >>> result = auth.login_user({
        ...     'email': 'john@example.com',
        ...     'password': 'securepassword123'
        ... })
        >>> print(f"Login successful: {bool(result['token'])}")
        Login successful: True
    """

    def __init__(self):
        """
        Initialize the AuthFacade with a UserRepository instance.

        The UserRepository is used for database operations related to user management.
        """
        self.user_repository = UserRepository()

    def register_user(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Register a new user with validation and persistence.

        This method handles the complete user registration process, including:
        - Required field validation
        - Email uniqueness check
        - Password hashing
        - Database persistence

        Args:
            data (Dict[str, Any]): Dictionary containing user registration data:
                - name (str): Full name of the user
                - email (str): Email address of the user
                - password (str): Plain-text password

        Returns:
            Dict[str, str]: Dictionary containing a success message.

        Raises:
            ValidationException: If required fields are missing or email is already registered.
            Exception: For any other database or system errors.

        Example:
            >>> auth = AuthFacade()
            >>> result = auth.register_user({
            ...     'name': 'John Doe',
            ...     'email': 'john@example.com',
            ...     'password': 'securepassword123'
            ... })
            >>> print(result['message'])
            User registered successfully.
        """
        try:
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            if not all([name, email, password]):
                raise ValidationException("Name, email and password are required.")

            if self.user_repository.get_by_email(email):
                raise ValidationException("Email is already registered.")

            # Create a new User and use set_password internally
            new_user = User(name=name, email=email, password=password)

            # Save to database using SQLAlchemy
            db.session.add(new_user)
            db.session.commit()

            return {"message": "User registered successfully."}
        except Exception as e:
            db.session.rollback()
            raise e

    def login_user(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Authenticate a user and generate a JWT token.

        This method handles the user login process, including:
        - Credential validation
        - Password verification
        - JWT token generation

        Args:
            data (Dict[str, Any]): Dictionary containing login credentials:
                - email (str): User's email address
                - password (str): User's password

        Returns:
            Dict[str, str]: Dictionary containing the JWT token.

        Raises:
            ValidationException: If credentials are missing or invalid.
            Exception: For any other system errors.

        Example:
            >>> auth = AuthFacade()
            >>> result = auth.login_user({
            ...     'email': 'john@example.com',
            ...     'password': 'securepassword123'
            ... })
            >>> print(f"Token generated: {bool(result['token'])}")
            Token generated: True
        """
        try:
            email = data.get('email')
            password = data.get('password')

            if not all([email, password]):
                raise ValidationException("Email and password are required.")

            user = self.user_repository.get_by_email(email)

            if not user or not user.check_password(password):
                raise ValidationException("Invalid credentials.")

            token = generate_jwt({"user_id": user.id, "email": user.email})
            return {"token": token}
        except Exception as e:
            raise e
