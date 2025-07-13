"""
Base repository class for common database operations.

Implements the Repository pattern using instance methods
to provide reusable CRUD operations for SQLAlchemy models.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Union, List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import and_, or_, func
from app.extensions import db

T = TypeVar("T")  # Tipo genérico para modelos SQLAlchemy


class IRepository(Generic[T], ABC):
    """
    Abstract interface for repository operations.
    
    This interface defines the contract that all repositories must implement.
    It provides basic CRUD operations and common query methods.
    """

    @abstractmethod
    def get_by_id(self, id_: int) -> Optional[T]:
        """Retrieve an entity by primary key."""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Return all instances of the model."""
        pass

    @abstractmethod
    def create(self, **kwargs) -> T:
        """Create a new entity instance."""
        pass

    @abstractmethod
    def update(self, entity: T, **updates) -> T:
        """Update an entity with new values."""
        pass

    @abstractmethod
    def delete(self, entity: T) -> bool:
        """Delete an entity from the database."""
        pass

    @abstractmethod
    def find_by(self, **filters) -> List[T]:
        """Find entities by filters."""
        pass

    @abstractmethod
    def find_one_by(self, **filters) -> Optional[T]:
        """Find one entity by filters."""
        pass

    @abstractmethod
    def count(self, **filters) -> int:
        """Count entities by filters."""
        pass

    @abstractmethod
    def exists(self, **filters) -> bool:
        """Check if entity exists by filters."""
        pass


class BaseRepository(IRepository[T]):
    """
    Abstract base repository for SQLAlchemy models.

    Subclasses must define the `model` class attribute.

    Example:
        >>> class UserRepository(BaseRepository[User]):
        ...     model = User
    """

    def __init__(self):
        self.db = db

    def get_by_id(self, id_: Union[int, str]) -> Optional[T]:
        """Retrieve an entity by primary key."""
        return self.db.session.query(self.model).get(id_)

    def get_all(self) -> List[T]:
        """Return all instances of the model."""
        return self.db.session.query(self.model).all()

    def create(self, **kwargs) -> T:
        """Create a new entity instance."""
        try:
            entity = self.model(**kwargs)
            self.db.session.add(entity)
            self.db.session.commit()
            return entity
        except Exception as e:
            self.db.session.rollback()
            raise e

    def update(self, entity: T, **updates) -> T:
        """Update an entity with new values."""
        try:
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            # Update timestamp if exists
            if hasattr(entity, 'updated_at'):
                entity.updated_at = datetime.utcnow()
            
            self.db.session.commit()
            return entity
        except Exception as e:
            self.db.session.rollback()
            raise e

    def delete(self, entity: T) -> bool:
        """Delete an entity from the database."""
        try:
            self.db.session.delete(entity)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            raise e

    def find_by(self, **filters) -> List[T]:
        """Find entities by filters."""
        query = self.db.session.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.all()

    def find_one_by(self, **filters) -> Optional[T]:
        """Find one entity by filters."""
        query = self.db.session.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.first()

    def count(self, **filters) -> int:
        """Count entities by filters."""
        query = self.db.session.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.count()

    def exists(self, **filters) -> bool:
        """Check if entity exists by filters."""
        return self.count(**filters) > 0