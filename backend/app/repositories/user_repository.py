"""
User repository for managing user data operations.

This module provides a repository class for managing user-related database operations.
It extends the BaseRepository class to provide user-specific functionality while
inheriting common CRUD operations.

The repository supports:
- User creation and management
- Email-based user lookup
- Email existence checking
- Password reset operations
- User status management
- Integration with User model
- Type-safe operations

Example:
    >>> user_repo = UserRepository()
    >>> user = user_repo.get_by_email("john@example.com")
    >>> if user:
    ...     print(f"Found user: {user.name}")
    ... else:
    ...     print("User not found")
    Found user: John Doe
"""

from typing import Optional, List, Dict, Any
from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app.extensions import db


class UserRepository(BaseRepository[User]):
    """
    Repository class for managing user data operations.

    This class extends BaseRepository to provide user-specific database operations.
    It implements additional methods for user management while inheriting common
    CRUD operations from the base class.

    Attributes:
        model (Type[User]): The User model class that this repository operates on.

    Example:
        >>> user_repo = UserRepository()
        >>> user = user_repo.get_by_email("john@example.com")
        >>> if user:
        ...     print(f"Found user: {user.name}")
        ... else:
        ...     print("User not found")
        Found user: John Doe
    """

    model = User

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.

        Args:
            email (str): The email address to search for.

        Returns:
            Optional[User]: The found user or None if not found.

        Example:
            >>> user = UserRepository.get_by_email("john@example.com")
            >>> if user:
            ...     print(f"Found user: {user.name}")
            ... else:
            ...     print("User not found")
            Found user: John Doe
        """
        return User.query.filter_by(email=email).first()

    @staticmethod
    def exists_by_email(email: str) -> bool:
        """
        Check if a user exists with the given email address.

        This method performs an efficient existence check without loading
        the full user record.

        Args:
            email (str): The email address to check.

        Returns:
            bool: True if a user exists with the given email, False otherwise.

        Example:
            >>> exists = UserRepository.exists_by_email("john@example.com")
            >>> if exists:
            ...     print("User exists")
            ... else:
            ...     print("User does not exist")
            User exists
        """
        return db.session.query(User.query.filter_by(email=email).exists()).scalar()
        