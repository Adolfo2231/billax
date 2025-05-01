"""
User Facade for managing user operations.

This module provides a facade class that handles business logic related to user management.
It acts as an intermediary between the API layer and the database, managing:
- User creation and validation
- User retrieval and authentication
- Plaid access token management
- Error handling and data persistence

The facade pattern is used to provide a simplified interface to complex subsystems,
hiding implementation details and providing a clean API for the rest of the application.

Example:
    >>> from app.facade.user_facade import UserFacade
    >>> # Create a new user
    >>> user = UserFacade.create_user(
    ...     name="John Doe",
    ...     email="john@example.com",
    ...     password="securepassword123"
    ... )
    >>> print(f"Created user: {user.name}")
"""

from typing import Union, Optional
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.exceptions.exceptions import (
    InvalidNameError,
    InvalidEmailError,
    InvalidPasswordError,
    DuplicateEmailError
)


class UserFacade:
    """
    Business logic layer for handling user operations.

    This class provides a simplified interface for managing users in the system.
    It handles all business logic related to users, including creation, validation,
    retrieval, and integration with external services like Plaid.

    Example:
        >>> # Create and retrieve a user
        >>> user = UserFacade.create_user(
        ...     name="John Doe",
        ...     email="john@example.com",
        ...     password="securepassword123"
        ... )
        >>> retrieved_user = UserFacade.get_user_by_email("john@example.com")
        >>> print(f"Found user: {retrieved_user.name}")
        Found user: John Doe
    """

    @staticmethod
    def create_user(name: str, email: str, password: str) -> User:
        """
        Creates a new user with validation and persistence.

        This method handles the complete user creation process, including:
        - Email uniqueness validation
        - Name format validation
        - Email format validation
        - Password strength validation
        - Database persistence

        Args:
            name (str): Full name of the user.
            email (str): Email address of the user.
            password (str): Plain-text password.

        Returns:
            User: The created user object.

        Raises:
            DuplicateEmailError: If the email is already registered.
            InvalidNameError: If the name format is invalid.
            InvalidEmailError: If the email format is invalid.
            InvalidPasswordError: If the password is too short.

        Example:
            >>> user = UserFacade.create_user(
            ...     name="John Doe",
            ...     email="john@example.com",
            ...     password="securepassword123"
            ... )
            >>> print(f"Created user: {user.name} - {user.email}")
            Created user: John Doe - john@example.com
        """
        if UserRepository.exists_by_email(email):
            raise DuplicateEmailError("Email already exists.")

        try:
            user = User(name=name, email=email, password=password)
            UserRepository.save(user)
            return user
        except IntegrityError:
            db.session.rollback()
            raise DuplicateEmailError("Email already exists (conflict during commit).")

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Fetch a user by email.

        This method retrieves a user from the database using their email address.
        It's commonly used for authentication and user lookup operations.

        Args:
            email (str): The user's email address.

        Returns:
            Optional[User]: The user if found, None otherwise.

        Example:
            >>> user = UserFacade.get_user_by_email("john@example.com")
            >>> if user:
            ...     print(f"Found user: {user.name}")
            ... else:
            ...     print("User not found")
            Found user: John Doe
        """
        return UserRepository.get_by_email(email)

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """
        Fetch a user by UUID.

        This method retrieves a user from the database using their unique identifier.
        It's commonly used for user management and profile operations.

        Args:
            user_id (str): The UUID of the user.

        Returns:
            Optional[User]: The user if found, None otherwise.

        Example:
            >>> user = UserFacade.get_user_by_id("user-123")
            >>> if user:
            ...     print(f"Found user: {user.name}")
            ... else:
            ...     print("User not found")
            Found user: John Doe
        """
        return UserRepository.get_by_id(user_id)

    @staticmethod
    def update_plaid_access_token(user_id: str, access_token: str) -> None:
        """
        Stores the Plaid access token for the given user.

        This method updates a user's Plaid access token, which is used for
        authenticating with the Plaid API and accessing financial data.

        Args:
            user_id (str): The ID of the user.
            access_token (str): The Plaid access token to store.

        Raises:
            ValueError: If the user is not found.

        Example:
            >>> UserFacade.update_plaid_access_token(
            ...     "user-123",
            ...     "access-sandbox-1234567890"
            ... )
            >>> user = UserFacade.get_user_by_id("user-123")
            >>> print(f"User linked to Plaid: {bool(user.plaid_access_token)}")
            User linked to Plaid: True
        """
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")

        user.plaid_access_token = access_token
        db.session.commit()
