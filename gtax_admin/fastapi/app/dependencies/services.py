"""
Service dependencies for dependency injection.

Demonstrates:
- Service factory pattern
- Database session injection
- Lazy service instantiation
"""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.user_service import UserService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.auth_service import AuthService


async def get_user_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserService:
    """
    Get UserService instance with injected database session.
    
    Args:
        db: Database session from get_db dependency
        
    Returns:
        UserService: Configured service instance
    """
    return UserService(db)


async def get_project_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ProjectService:
    """
    Get ProjectService instance with injected database session.
    
    Args:
        db: Database session from get_db dependency
        
    Returns:
        ProjectService: Configured service instance
    """
    return ProjectService(db)


async def get_task_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> TaskService:
    """
    Get TaskService instance with injected database session.
    
    Args:
        db: Database session from get_db dependency
        
    Returns:
        TaskService: Configured service instance
    """
    return TaskService(db)


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AuthService:
    """
    Get AuthService instance with injected database session.
    
    Args:
        db: Database session from get_db dependency
        
    Returns:
        AuthService: Configured service instance
    """
    return AuthService(db)
