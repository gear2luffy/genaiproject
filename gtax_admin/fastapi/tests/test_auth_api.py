"""
Integration tests for Authentication API endpoints.

Demonstrates:
- API endpoint testing
- Authentication flow testing
- Request/response validation
"""

import pytest
from httpx import AsyncClient

from app.models.user import User


class TestAuthEndpoints:
    """Integration tests for /api/v1/auth endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient):
        """Test user registration endpoint."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser123",
                "password": "SecurePass123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser123"
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "username": "testuser",
                "password": "weak"  # Too short, no uppercase, no digit
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test registration with existing email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "username": "differentuser",
                "password": "SecurePass123"
            }
        )
        
        assert response.status_code == 409  # Conflict
        assert "Email already registered" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_login_success(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,  # OAuth2 uses 'username' field
                "password": "TestPass123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_json_success(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test successful login with JSON body."""
        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": test_user.email,
                "password": "TestPass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test login with wrong password."""
        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": test_user.email,
                "password": "WrongPassword123"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePass123"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test getting current user profile."""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test accessing protected endpoint without token."""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test accessing protected endpoint with invalid token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_refresh_token(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test token refresh."""
        # First, login to get tokens
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": test_user.email,
                "password": "TestPass123"
            }
        )
        
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_change_password(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test password change."""
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "TestPass123",
                "new_password": "NewSecurePass456"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify new password works
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": test_user.email,
                "password": "NewSecurePass456"
            }
        )
        assert login_response.status_code == 200
