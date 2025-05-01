"""
Base repository class for common database operations.

This module provides an abstract base class that defines common database operations
that can be reused across different repositories. It implements the Repository pattern
and provides a generic interface for CRUD operations on SQLAlchemy models.

The base repository supports:
- Generic type support for different SQLAlchemy models
- Common CRUD operations (Create, Read, Update, Delete)
- Type-safe operations with proper type hints
- Session management and transaction handling

Example:
    >>> class UserRepository(BaseRepository[User]):
    ...     model = User
    ...
    ...     @classmethod
    ...     def get_by_email(cls, email: str) -> Optional[User]:
    ...         return cls.model.query.filter_by(email=email).first()
    ...
    >>> user_repo = UserRepository()
    >>> user = user_repo.get_by_id("user-123")
    >>> user.name
    'John Doe'
"""

from typing import TypeVar, Generic, Type, Union, List, Optional, Any
from app.extensions import db
from sqlalchemy.orm import Query

T = TypeVar("T")  # Type of the SQLAlchemy model


class BaseRepository(Generic[T]):
    """
    Base repository class providing common CRUD operations for SQLAlchemy models.

    This class serves as a base implementation of the Repository pattern,
    providing common database operations that can be reused across different
    repositories. It uses generics to ensure type safety and proper IDE support.

    Subclasses must define the `model` class attribute to specify which
    SQLAlchemy model they operate on.

    Attributes:
        model (Type[T]): The SQLAlchemy model class that this repository operates on.
                        Must be overridden in subclasses.

    Example:
        >>> class UserRepository(BaseRepository[User]):
        ...     model = User
        ...
        ...     @classmethod
        ...     def get_by_email(cls, email: str) -> Optional[User]:
        ...         return cls.model.query.filter_by(email=email).first()
        ...
        >>> user_repo = UserRepository()
        >>> user = user_repo.get_by_id("user-123")
        >>> user.name
        'John Doe'
    """

    model: Type[T] = None  # Should be overridden in subclass

    @classmethod
    def get_by_id(cls, id_: Union[str, int]) -> Optional[T]:
        """
        Retrieve an entity by its primary key.

        Args:
            id_ (Union[str, int]): The UUID or primary key of the entity.

        Returns:
            Optional[T]: The found entity or None if not found.

        Example:
            >>> user = UserRepository.get_by_id("user-123")
            >>> if user:
            ...     print(f"Found user: {user.name}")
            ... else:
            ...     print("User not found")
            Found user: John Doe
        """
        return cls.model.query.get(id_)

    @classmethod
    def get_all(cls) -> List[T]:
        """
        Retrieve all records of the model.

        Returns:
            List[T]: List of all model instances.

        Example:
            >>> users = UserRepository.get_all()
            >>> for user in users:
            ...     print(f"User: {user.name}")
            User: John Doe
            User: Jane Smith
        """
        return cls.model.query.all()

    @classmethod
    def save(cls, entity: T) -> None:
        """
        Persist the given entity to the database.

        This method adds the entity to the current session and commits
        the transaction. If the entity already exists, it will be updated.

        Args:
            entity (T): The entity to persist.

        Example:
            >>> user = User(name="John Doe", email="john@example.com")
            >>> UserRepository.save(user)
            >>> saved_user = UserRepository.get_by_id(user.id)
            >>> saved_user.name
            'John Doe'
        """
        db.session.add(entity)
        db.session.commit()

    @classmethod
    def delete(cls, entity: T) -> None:
        """
        Delete the given entity from the database.

        This method removes the entity from the current session and commits
        the transaction.

        Args:
            entity (T): The entity to delete.

        Example:
            >>> user = UserRepository.get_by_id("user-123")
            >>> UserRepository.delete(user)
            >>> deleted_user = UserRepository.get_by_id("user-123")
            >>> deleted_user is None
            True
        """
        db.session.delete(entity)
        db.session.commit()

    @classmethod
    def query(cls) -> Query:
        """
        Get a query object for the model.

        This method provides access to SQLAlchemy's query interface,
        allowing for more complex queries to be constructed.

        Returns:
            Query: A SQLAlchemy query object for the model.

        Example:
            >>> query = UserRepository.query()
            >>> active_users = query.filter_by(is_active=True).all()
            >>> for user in active_users:
            ...     print(f"Active user: {user.name}")
            Active user: John Doe
        """
        return cls.model.query
