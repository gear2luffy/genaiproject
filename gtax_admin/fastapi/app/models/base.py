"""
Base model with common fields and functionality.

Demonstrates:
- OOP inheritance for models
- Reusable mixins
- SQLAlchemy 2.0 mapped_column syntax
"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamps.
    
    Demonstrates:
    - Mixin pattern for reusable model fields
    - Server-side defaults with SQLAlchemy
    - Automatic timestamp updates
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the record was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when the record was last updated"
    )


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality.
    
    Instead of permanently deleting records, this marks them
    as deleted while keeping the data for audit purposes.
    """
    
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        doc="Soft delete flag"
    )
    
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when the record was soft deleted"
    )
    
    def soft_delete(self) -> None:
        """Mark the record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None


class BaseModelMixin(TimestampMixin):
    """
    Combined base mixin with all common functionality.
    
    Includes:
    - Timestamps (created_at, updated_at)
    - Utility methods
    """
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update(self, **kwargs: Any) -> None:
        """
        Update model attributes from keyword arguments.
        
        Args:
            **kwargs: Attribute names and values to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
