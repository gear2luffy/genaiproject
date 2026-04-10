"""
User service for user management operations.

Demonstrates:
- Service layer pattern
- Business logic encapsulation
- Repository composition
- Async operations
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import BaseRepository
from app.core.security import security_service
from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository for User model with specialized queries."""
    
    def __init__(self, db: AsyncSession) -> None:
        """Initialize with User model."""
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: The email to search for
            
        Returns:
            Optional[User]: The user or None
        """
        query = select(User).where(User.email == email)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: The username to search for
            
        Returns:
            Optional[User]: The user or None
        """
        query = select(User).where(User.username == username)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get all active users with pagination."""
        query = (
            select(User)
            .where(User.is_active == True)  # noqa: E712
            .where(User.is_deleted == False)  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def search_users(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[User], int]:
        """
        Search users by email, username, or full name.
        
        Args:
            search_term: Search query string
            skip: Pagination offset
            limit: Maximum results
            
        Returns:
            Tuple of users list and total count
        """
        search_pattern = f"%{search_term}%"
        
        base_query = select(User).where(
            or_(
                User.email.ilike(search_pattern),
                User.username.ilike(search_pattern),
                User.full_name.ilike(search_pattern)
            ),
            User.is_deleted == False  # noqa: E712
        )
        
        # Count query
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self._db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Data query with pagination
        data_query = base_query.offset(skip).limit(limit)
        data_result = await self._db.execute(data_query)
        users = list(data_result.scalars().all())
        
        return users, total
    
    async def count_by_role(self, role: UserRole) -> int:
        """Count users by role."""
        query = select(func.count()).select_from(User).where(
            User.role == role,
            User.is_deleted == False  # noqa: E712
        )
        result = await self._db.execute(query)
        return result.scalar() or 0


class UserService:
    """
    Service class for user management.
    
    Demonstrates:
    - Service layer pattern
    - Business logic and validation
    - Repository composition
    - Transaction management
    """
    
    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize user service.
        
        Args:
            db: Async database session
        """
        self._db = db
        self._repository = UserRepository(db)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user with validation.
        
        Args:
            user_data: User creation schema
            
        Returns:
            User: The created user
            
        Raises:
            ConflictError: If email or username already exists
        """
        # Check for existing email
        if await self._repository.get_by_email(user_data.email):
            raise ConflictError(
                message="Email already registered",
                resource="User",
                details={"email": user_data.email}
            )
        
        # Check for existing username
        if await self._repository.get_by_username(user_data.username):
            raise ConflictError(
                message="Username already taken",
                resource="User",
                details={"username": user_data.username}
            )
        
        # Hash password
        hashed_password = security_service.hash_password(user_data.password)
        
        # Create user
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["hashed_password"] = hashed_password
        
        user = await self._repository.create(user_dict)
        logger.info("User created", user_id=user.id, email=user.email)
        
        return user
    
    async def get_user(self, user_id: int) -> User:
        """
        Get user by ID.
        
        Args:
            user_id: The user ID
            
        Returns:
            User: The user
            
        Raises:
            NotFoundError: If user not found
        """
        user = await self._repository.get_by_id(user_id)
        if not user or user.is_deleted:
            raise NotFoundError("User", user_id)
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return await self._repository.get_by_email(email)
    
    async def get_users(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None
    ) -> Tuple[List[User], int]:
        """
        Get users with optional search.
        
        Args:
            skip: Pagination offset
            limit: Maximum results
            search: Optional search term
            
        Returns:
            Tuple of users list and total count
        """
        if search:
            return await self._repository.search_users(search, skip, limit)
        
        users = await self._repository.get_active_users(skip, limit)
        total = await self._repository.count()
        return users, total
    
    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdate
    ) -> User:
        """
        Update user details.
        
        Args:
            user_id: The user ID
            user_data: Update schema
            
        Returns:
            User: The updated user
            
        Raises:
            NotFoundError: If user not found
            ConflictError: If email/username conflict
        """
        user = await self.get_user(user_id)
        
        # Check email conflict
        if user_data.email and user_data.email != user.email:
            existing = await self._repository.get_by_email(user_data.email)
            if existing:
                raise ConflictError(
                    message="Email already registered",
                    resource="User"
                )
        
        # Check username conflict
        if user_data.username and user_data.username != user.username:
            existing = await self._repository.get_by_username(user_data.username)
            if existing:
                raise ConflictError(
                    message="Username already taken",
                    resource="User"
                )
        
        # Hash new password if provided
        update_dict = user_data.model_dump(exclude_unset=True, exclude={"password"})
        if user_data.password:
            update_dict["hashed_password"] = security_service.hash_password(
                user_data.password
            )
        
        updated_user = await self._repository.update(user_id, update_dict)
        logger.info("User updated", user_id=user_id)
        
        return updated_user
    
    async def delete_user(self, user_id: int) -> bool:
        """
        Soft delete a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            bool: True if deleted
            
        Raises:
            NotFoundError: If user not found
        """
        user = await self.get_user(user_id)
        user.soft_delete()
        await self._db.flush()
        
        logger.info("User deleted", user_id=user_id)
        return True
    
    async def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp."""
        await self._repository.update(
            user_id,
            {"last_login_at": datetime.utcnow()}
        )
    
    async def verify_user(self, user_id: int) -> User:
        """Mark user as verified."""
        return await self._repository.update(
            user_id,
            {"is_verified": True}
        )
    
    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password with verification.
        
        Args:
            user_id: The user ID
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            bool: True if password changed
            
        Raises:
            NotFoundError: If user not found
            ValidationError: If current password is incorrect
        """
        from app.core.exceptions import ValidationError
        
        user = await self.get_user(user_id)
        
        # Verify current password
        if not security_service.verify_password(
            current_password,
            user.hashed_password
        ):
            raise ValidationError("Current password is incorrect")
        
        # Update password
        hashed_password = security_service.hash_password(new_password)
        await self._repository.update(
            user_id,
            {"hashed_password": hashed_password}
        )
        
        logger.info("Password changed", user_id=user_id)
        return True
