"""
Authentication dependencies for FastAPI.

Demonstrates:
- OAuth2 password flow
- JWT token validation
- Role-based access control
- Custom dependency injection
"""

from typing import Annotated, Callable, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.logging import get_logger

logger = get_logger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    description="JWT Bearer Token Authentication"
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    This dependency:
    1. Extracts the token from Authorization header
    2. Validates the JWT token
    3. Retrieves and returns the user
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user_from_token(token)
        return user
    except AuthenticationError as e:
        logger.warning("Authentication failed", error=str(e))
        raise credentials_exception


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get current user and verify they are active.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User: The active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Get current user and verify they are an admin.
    
    Args:
        current_user: Active user
        
    Returns:
        User: The admin user
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_manager_or_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Get current user and verify they are a manager or admin.
    
    Args:
        current_user: Active user
        
    Returns:
        User: The manager or admin user
        
    Raises:
        HTTPException: If user is neither manager nor admin
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin access required"
        )
    return current_user


def require_permission(permission: str) -> Callable:
    """
    Create a dependency that checks for a specific permission.
    
    This is a dependency factory that creates a new dependency
    for checking a specific permission.
    
    Args:
        permission: The required permission string
        
    Returns:
        Callable: A dependency function
        
    Example:
        >>> @router.get("/admin/users")
        ... async def list_users(
        ...     user: User = Depends(require_permission("users:read"))
        ... ):
        ...     ...
    """
    async def permission_dependency(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        """Check if user has required permission."""
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    
    return permission_dependency


def require_any_permission(permissions: List[str]) -> Callable:
    """
    Create a dependency that checks for any of the specified permissions.
    
    Args:
        permissions: List of permission strings (user needs at least one)
        
    Returns:
        Callable: A dependency function
    """
    async def permission_dependency(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        """Check if user has any of the required permissions."""
        for permission in permissions:
            if current_user.has_permission(permission):
                return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"One of these permissions required: {', '.join(permissions)}"
        )
    
    return permission_dependency


class RoleChecker:
    """
    Callable class for role-based access control.
    
    Demonstrates:
    - Callable class pattern
    - Reusable role checking
    
    Example:
        >>> require_roles = RoleChecker([UserRole.ADMIN, UserRole.MANAGER])
        >>> @router.get("/manage")
        ... async def manage(user: User = Depends(require_roles)):
        ...     ...
    """
    
    def __init__(self, allowed_roles: List[UserRole]) -> None:
        """
        Initialize role checker with allowed roles.
        
        Args:
            allowed_roles: List of roles that are allowed access
        """
        self.allowed_roles = allowed_roles
    
    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        """
        Check if user's role is in allowed roles.
        
        Args:
            current_user: The authenticated user
            
        Returns:
            User: The user if authorized
            
        Raises:
            HTTPException: If user's role is not allowed
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {[r.value for r in self.allowed_roles]}"
            )
        return current_user


# Pre-defined role checkers
AdminOnly = RoleChecker([UserRole.ADMIN])
ManagerOrAdmin = RoleChecker([UserRole.ADMIN, UserRole.MANAGER])
AnyRole = RoleChecker([UserRole.ADMIN, UserRole.MANAGER, UserRole.USER])
