"""
Base repository class for common database operations.

Implements the Repository pattern using generics and class methods
to provide reusable CRUD operations for SQLAlchemy models.
"""

from typing import TypeVar, Generic, Type, Union, List, Optional
from app.extensions import db  # Asegúrate de tener db = SQLAlchemy() en extensions.py

T = TypeVar("T")  # Tipo genérico para modelos SQLAlchemy


class BaseRepository(Generic[T]):
    """
    Abstract base repository for SQLAlchemy models.

    Subclasses must define the `model` class attribute.

    Example:
        >>> class UserRepository(BaseRepository[User]):
        ...     model = User
    """

    model: Type[T] = None  # Debe ser sobrescrito por cada subclase
    
    def __init__(self):
        pass

    @classmethod
    def get_by_id(cls, id_: Union[int, str]) -> Optional[T]:
        """Retrieve an entity by primary key."""
        return cls.model.query.get(id_)

    @classmethod
    def get_all(cls) -> List[T]:
        """Return all instances of the model."""
        return cls.model.query.all()

    @classmethod
    def save(cls, entity: T) -> T:
        """
        Add or update an instance in the database.
        """
        db.session.add(entity)
        db.session.commit()
        return entity

    @classmethod
    def update(cls, entity: T) -> T:
        """
        Update an instance in the database.
        """
        db.session.add(entity)
        db.session.commit()
        return entity
    
    @classmethod
    def delete(cls, entity: T) -> None:
        """
        Delete an instance from the database.
        """
        db.session.delete(entity)
        db.session.commit()