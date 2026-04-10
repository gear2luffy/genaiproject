"""
Base repository pattern implementation.

Demonstrates:
- Repository pattern for data access
- Generic typing for reusability
- Async database operations
- CRUD abstraction
"""

from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import Base
from app.core.logging import get_logger

logger = get_logger(__name__)

# Generic type variable for model classes
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations.
    
    Demonstrates:
    - Generic class implementation
    - Repository pattern for data access layer
    - Async/await database operations
    - Separation of concerns
    
    Example:
        >>> class UserRepository(BaseRepository[User]):
        ...     def __init__(self, db: AsyncSession):
        ...         super().__init__(User, db)
    """
    
    def __init__(self, model: Type[ModelType], db: AsyncSession) -> None:
        """
        Initialize repository with model class and database session.
        
        Args:
            model: The SQLAlchemy model class
            db: Async database session
        """
        self._model = model
        self._db = db
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            id: The record ID
            
        Returns:
            Optional[ModelType]: The record or None if not found
        """
        query = select(self._model).where(self._model.id == id)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[ModelType]: List of records
        """
        query = select(self._model).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """
        Get total count of records.
        
        Returns:
            int: Total number of records
        """
        query = select(func.count()).select_from(self._model)
        result = await self._db.execute(query)
        return result.scalar() or 0
    
    async def create(self, obj_data: dict[str, Any]) -> ModelType:
        """
        Create a new record.
        
        Args:
            obj_data: Dictionary of field values
            
        Returns:
            ModelType: The created record
        """
        db_obj = self._model(**obj_data)
        self._db.add(db_obj)
        await self._db.flush()
        await self._db.refresh(db_obj)
        logger.debug(
            "Created record",
            model=self._model.__name__,
            id=db_obj.id
        )
        return db_obj
    
    async def update(
        self,
        id: int,
        obj_data: dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Update an existing record.
        
        Args:
            id: The record ID
            obj_data: Dictionary of fields to update
            
        Returns:
            Optional[ModelType]: The updated record or None
        """
        # Remove None values for partial updates
        update_data = {k: v for k, v in obj_data.items() if v is not None}
        
        if not update_data:
            return await self.get_by_id(id)
        
        query = (
            update(self._model)
            .where(self._model.id == id)
            .values(**update_data)
        )
        await self._db.execute(query)
        await self._db.flush()
        
        logger.debug(
            "Updated record",
            model=self._model.__name__,
            id=id
        )
        return await self.get_by_id(id)
    
    async def delete(self, id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id: The record ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        query = delete(self._model).where(self._model.id == id)
        result = await self._db.execute(query)
        await self._db.flush()
        
        deleted = result.rowcount > 0
        if deleted:
            logger.debug(
                "Deleted record",
                model=self._model.__name__,
                id=id
            )
        return deleted
    
    async def exists(self, id: int) -> bool:
        """
        Check if a record exists.
        
        Args:
            id: The record ID
            
        Returns:
            bool: True if exists, False otherwise
        """
        query = select(func.count()).select_from(self._model).where(
            self._model.id == id
        )
        result = await self._db.execute(query)
        return (result.scalar() or 0) > 0
    
    async def bulk_create(
        self,
        objects_data: List[dict[str, Any]]
    ) -> List[ModelType]:
        """
        Create multiple records in bulk.
        
        Args:
            objects_data: List of dictionaries with field values
            
        Returns:
            List[ModelType]: List of created records
        """
        db_objects = [self._model(**data) for data in objects_data]
        self._db.add_all(db_objects)
        await self._db.flush()
        
        for obj in db_objects:
            await self._db.refresh(obj)
        
        logger.debug(
            "Bulk created records",
            model=self._model.__name__,
            count=len(db_objects)
        )
        return db_objects
