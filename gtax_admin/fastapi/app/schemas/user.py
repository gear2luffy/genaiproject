"""
User-related Pydantic schemas.

Demonstrates:
- Schema inheritance (base → create → update → response)
- Field validation with constraints
- Nested models
- Password validation
- Email validation
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole
from app.schemas.common import BaseSchema


class UserBase(BaseSchema):
    """
    Base user schema with shared fields.
    
    This schema contains fields that are common across
    create, update, and response schemas.
    """
    
    email: EmailStr = Field(
        description="User email address",
        examples=["user@example.com"]
    )
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username (alphanumeric, underscore, hyphen)",
        examples=["john_doe"]
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="User's full name",
        examples=["John Doe"]
    )


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    
    Demonstrates:
    - Password validation with custom rules
    - Inheritance from base schema
    """
    
    password: str = Field(
        min_length=8,
        max_length=100,
        description="User password (min 8 chars, must contain letter and number)",
        examples=["SecurePass123"]
    )
    role: UserRole = Field(
        default=UserRole.USER,
        description="User role for authorization"
    )
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets security requirements.
        
        Args:
            v: The password to validate
            
        Returns:
            str: The validated password
            
        Raises:
            ValueError: If password doesn't meet requirements
        """
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseSchema):
    """
    Schema for updating an existing user.
    
    All fields are optional to support partial updates.
    """
    
    email: Optional[EmailStr] = Field(
        default=None,
        description="New email address"
    )
    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="New username"
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="New full name"
    )
    password: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=100,
        description="New password"
    )
    role: Optional[UserRole] = Field(
        default=None,
        description="New role (admin only)"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Account active status"
    )
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: Optional[str]) -> Optional[str]:
        """Validate password if provided."""
        if v is None:
            return v
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponse(UserBase):
    """
    Schema for user responses (public user data).
    
    Excludes sensitive fields like password hash.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(description="User ID")
    role: UserRole = Field(description="User role")
    is_active: bool = Field(description="Account active status")
    is_verified: bool = Field(description="Email verified status")
    created_at: datetime = Field(description="Account creation timestamp")
    last_login_at: Optional[datetime] = Field(
        default=None,
        description="Last login timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "john_doe",
                "full_name": "John Doe",
                "role": "user",
                "is_active": True,
                "is_verified": True,
                "created_at": "2025-01-01T00:00:00Z",
                "last_login_at": "2025-01-10T12:00:00Z"
            }
        }


class UserInDB(UserResponse):
    """
    Schema for user with database fields (internal use).
    
    Includes password hash for authentication purposes.
    """
    
    hashed_password: str = Field(description="Hashed password")


# Authentication Schemas

class UserLogin(BaseModel):
    """Schema for user login request."""
    
    email: EmailStr = Field(
        description="User email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        description="User password",
        examples=["SecurePass123"]
    )


class Token(BaseModel):
    """Schema for JWT token response."""
    
    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class TokenPayload(BaseModel):
    """Schema for decoded JWT token payload."""
    
    sub: str = Field(description="Subject (user ID)")
    exp: datetime = Field(description="Expiration timestamp")
    type: str = Field(description="Token type (access/refresh)")
    role: Optional[str] = Field(default=None, description="User role")


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    
    refresh_token: str = Field(description="Refresh token")


class PasswordChange(BaseModel):
    """Schema for password change request."""
    
    current_password: str = Field(description="Current password")
    new_password: str = Field(
        min_length=8,
        max_length=100,
        description="New password"
    )
    
    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate new password meets security requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserListResponse(BaseSchema):
    """Schema for paginated user list response."""
    
    items: List[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int
