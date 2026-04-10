"""
Unit tests for User service.

Demonstrates:
- Service layer testing
- Mocking dependencies
- Async test patterns
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.user_service import UserService, UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User, UserRole
from app.core.exceptions import NotFoundError, ConflictError


class TestUserService:
    """Tests for UserService class."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, test_db):
        """Test successful user creation."""
        service = UserService(test_db)
        
        user_data = UserCreate(
            email="newuser@example.com",
            username="newuser",
            password="SecurePass123",
            full_name="New User"
        )
        
        user = await service.create_user(user_data)
        
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.full_name == "New User"
        assert user.role == UserRole.USER
        assert user.is_active is True
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, test_db, test_user):
        """Test user creation with duplicate email."""
        service = UserService(test_db)
        
        user_data = UserCreate(
            email=test_user.email,  # Same email
            username="different_username",
            password="SecurePass123"
        )
        
        with pytest.raises(ConflictError) as exc_info:
            await service.create_user(user_data)
        
        assert "Email already registered" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, test_db, test_user):
        """Test user creation with duplicate username."""
        service = UserService(test_db)
        
        user_data = UserCreate(
            email="different@example.com",
            username=test_user.username,  # Same username
            password="SecurePass123"
        )
        
        with pytest.raises(ConflictError) as exc_info:
            await service.create_user(user_data)
        
        assert "Username already taken" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_user_success(self, test_db, test_user):
        """Test getting user by ID."""
        service = UserService(test_db)
        
        user = await service.get_user(test_user.id)
        
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, test_db):
        """Test getting non-existent user."""
        service = UserService(test_db)
        
        with pytest.raises(NotFoundError):
            await service.get_user(99999)
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, test_db, test_user):
        """Test successful user update."""
        service = UserService(test_db)
        
        update_data = UserUpdate(
            full_name="Updated Name"
        )
        
        updated_user = await service.update_user(test_user.id, update_data)
        
        assert updated_user.full_name == "Updated Name"
        assert updated_user.email == test_user.email  # Unchanged
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self, test_db, test_user):
        """Test soft delete user."""
        service = UserService(test_db)
        
        result = await service.delete_user(test_user.id)
        
        assert result is True
        
        # User should be soft deleted
        with pytest.raises(NotFoundError):
            await service.get_user(test_user.id)


class TestUserRepository:
    """Tests for UserRepository class."""
    
    @pytest.mark.asyncio
    async def test_get_by_email(self, test_db, test_user):
        """Test getting user by email."""
        repo = UserRepository(test_db)
        
        user = await repo.get_by_email(test_user.email)
        
        assert user is not None
        assert user.id == test_user.id
    
    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, test_db):
        """Test getting non-existent email."""
        repo = UserRepository(test_db)
        
        user = await repo.get_by_email("nonexistent@example.com")
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_by_username(self, test_db, test_user):
        """Test getting user by username."""
        repo = UserRepository(test_db)
        
        user = await repo.get_by_username(test_user.username)
        
        assert user is not None
        assert user.id == test_user.id
