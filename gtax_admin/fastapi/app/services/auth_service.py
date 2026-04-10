"""
Authentication service for login and token management.

Demonstrates:
- JWT token creation and validation
- User authentication flow
- Token refresh logic
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import Token, UserLogin
from app.services.user_service import UserService
from app.core.security import security_service
from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """
    Service class for authentication operations.
    
    Demonstrates:
    - User authentication
    - JWT token management
    - Session handling
    """
    
    def __init__(self, db: AsyncSession) -> None:
        """Initialize authentication service."""
        self._db = db
        self._user_service = UserService(db)
    
    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> User:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User: Authenticated user
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        user = await self._user_service.get_user_by_email(email)
        
        if not user:
            logger.warning("Login attempt with unknown email", email=email)
            raise AuthenticationError("Invalid email or password")
        
        if not security_service.verify_password(password, user.hashed_password):
            logger.warning("Invalid password attempt", user_id=user.id)
            raise AuthenticationError("Invalid email or password")
        
        if not user.is_active:
            logger.warning("Login attempt by inactive user", user_id=user.id)
            raise AuthenticationError("Account is disabled")
        
        if user.is_deleted:
            raise AuthenticationError("Account has been deleted")
        
        # Update last login
        await self._user_service.update_last_login(user.id)
        
        logger.info("User authenticated", user_id=user.id, email=email)
        return user
    
    async def login(self, credentials: UserLogin) -> Token:
        """
        Perform user login and return tokens.
        
        Args:
            credentials: Login credentials
            
        Returns:
            Token: Access and refresh tokens
        """
        user = await self.authenticate_user(
            email=credentials.email,
            password=credentials.password
        )
        
        # Create token payload
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        }
        
        # Generate tokens
        tokens = security_service.create_token_pair(token_data)
        
        return Token(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    async def refresh_access_token(self, refresh_token: str) -> Token:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Token: New access and refresh tokens
            
        Raises:
            AuthenticationError: If refresh token is invalid
        """
        # Decode and validate refresh token
        payload = security_service.decode_token(refresh_token)
        
        if not payload:
            raise AuthenticationError("Invalid refresh token")
        
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")
        
        # Get user
        user_id = int(payload.get("sub", 0))
        try:
            user = await self._user_service.get_user(user_id)
        except Exception:
            raise AuthenticationError("User not found")
        
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        
        # Create new tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        }
        
        tokens = security_service.create_token_pair(token_data)
        
        logger.info("Token refreshed", user_id=user.id)
        
        return Token(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    def validate_access_token(self, token: str) -> Optional[dict]:
        """
        Validate an access token.
        
        Args:
            token: The access token to validate
            
        Returns:
            Optional[dict]: Token payload or None if invalid
        """
        payload = security_service.decode_token(token)
        
        if not payload:
            return None
        
        if payload.get("type") != "access":
            return None
        
        return payload
    
    async def get_current_user_from_token(self, token: str) -> User:
        """
        Get current user from access token.
        
        Args:
            token: Valid access token
            
        Returns:
            User: The authenticated user
            
        Raises:
            AuthenticationError: If token is invalid
        """
        payload = self.validate_access_token(token)
        
        if not payload:
            raise AuthenticationError("Invalid or expired token")
        
        user_id = int(payload.get("sub", 0))
        
        try:
            user = await self._user_service.get_user(user_id)
        except Exception:
            raise AuthenticationError("User not found")
        
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        
        return user
