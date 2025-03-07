import json
import typing
from datetime import datetime

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class BaseMixin:
    """
    Base mixin providing common columns and serialization functionality for SQLAlchemy models.
    
    Provides automatic ID generation, timestamp tracking, and standardized serialization.
    Ensures proper table naming conventions and implements abstract base class pattern.
    
    Attributes:
        id (Column): Auto-incrementing primary key
        created_at (Column): Timestamp when record was created
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __init_subclass__(cls):
        """
        Validates subclass configuration during class creation.
        
        Ensures subclasses define proper table naming and implements required methods.
        
        Raises:
            ValueError: If __tablename__ is missing or invalid
        """
        if not hasattr(cls, '__abstract__') or not cls.__abstract__:
            if not hasattr(cls, '__tablename__'):
                raise ValueError(f"The class {cls.__name__} must define __tablename__")
            if not isinstance(cls.__tablename__, str) or not cls.__tablename__.strip():
                raise ValueError(f"__tablename__ must be a non-empty string in {cls.__name__}")

    @property
    def dumps(self) -> str:
        """
        Serialize the object to a JSON string.
        
        Combines base attributes with model-specific fields defined in _to_dict().
        
        Returns:
            str: JSON representation of the object
        """
        return json.dumps({
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            **self._to_dict()
        })

    def _to_dict(self) -> typing.Dict[str, typing.Any]:
        """
        Convert object attributes to dictionary format.
        
        Must be implemented by subclasses to include model-specific fields.
        
        Raises:
            NotImplementedError: Always, forcing subclasses to implement
        
        Returns:
            Dict[str, Any]: Dictionary representation of model-specific fields
        """
        raise NotImplementedError(f"The _to_dict method must be implemented in {self.__class__.__name__}")


class BaseDocument(BaseMixin, Base):
    """
    Abstract base document class combining SQLAlchemy declarative base with BaseMixin.
    
    Provides foundation for document-based models with automatic timestamp handling.
    
    Attributes:
        created_at (DateTime): Timestamp when record was created
    """
    __abstract__ = True
    __tablename__ = None

    def __init__(self):
        """
        Initialize the document with current timestamp.
        
        Sets created_at to current time using database server's clock.
        """
        self.created_at = datetime.now()
        super().__init__()