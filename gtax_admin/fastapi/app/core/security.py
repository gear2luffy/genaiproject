"""
Security utilities for authentication and authorization.

Demonstrates:
- OOP with classes and inheritance
- Password hashing with bcrypt
- JWT token creation and validation
- Type hints throughout
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


class SecurityService:
    """
    Service class for handling security operations.
    
    Demonstrates:
    - Encapsulation of security logic
    - Class-based service pattern
    - Context manager usage with passlib
    """
    
    def __init__(
        self,
        secret_key: str = settings.secret_key,
        algorithm: str = settings.algorithm,
        access_token_expire_minutes: int = settings.access_token_expire_minutes,
        refresh_token_expire_days: int = settings.refresh_token_expire_days
    ) -> None:
        """
        Initialize security service with configuration.
        
        Args:
            secret_key: Secret key for JWT encoding
            algorithm: JWT algorithm to use
            access_token_expire_minutes: Access token expiration time
            refresh_token_expire_days: Refresh token expiration time
        """
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days
        
        # Password hashing context using bcrypt
        self._pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto"
        )
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.
        
        Args:
            plain_password: The plain text password to verify
            hashed_password: The hashed password to compare against
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return self._pwd_context.verify(plain_password, hashed_password)
    
    def hash_password(self, password: str) -> str:
        """
        Hash a plain password using bcrypt.
        
        Args:
            password: The plain text password to hash
            
        Returns:
            str: The hashed password
        """
        return self._pwd_context.hash(password)
    
    def create_access_token(
        self,
        data: dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self._access_token_expire_minutes
            )
        
        to_encode.update({
            "exp": expire,
            "type": "access"
        })
        
        return jwt.encode(
            to_encode,
            self._secret_key,
            algorithm=self._algorithm
        )
    
    def create_refresh_token(
        self,
        data: dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT refresh token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            str: Encoded JWT refresh token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=self._refresh_token_expire_days
            )
        
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })
        
        return jwt.encode(
            to_encode,
            self._secret_key,
            algorithm=self._algorithm
        )
    
    def decode_token(self, token: str) -> Optional[dict[str, Any]]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: The JWT token to decode
            
        Returns:
            Optional[dict]: Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm]
            )
            return payload
        except JWTError:
            return None
    
    def create_token_pair(self, data: dict[str, Any]) -> dict[str, str]:
        """
        Create both access and refresh tokens.
        
        Args:
            data: Data to encode in the tokens
            
        Returns:
            dict: Dictionary containing access_token and refresh_token
        """
        return {
            "access_token": self.create_access_token(data),
            "refresh_token": self.create_refresh_token(data),
            "token_type": "bearer"
        }


# Global security service instance
security_service = SecurityService()
