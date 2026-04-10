"""
User management endpoints.

Demonstrates:
- Full CRUD operations
- Pagination and filtering
- Role-based access control
- Response models
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
)
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.user_service import UserService
from app.dependencies.auth import (
    get_current_active_user,
    get_admin_user,
    require_permission,
)
from app.dependencies.services import get_user_service
from app.dependencies.pagination import get_pagination, PaginationParams
from app.models.user import User
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="List Users",
    description="Get paginated list of users. Requires users:read permission."
)
async def list_users(
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(require_permission("users:read"))],
    search: Annotated[
        Optional[str],
        Query(description="Search users by email, username, or name")
    ] = None
) -> PaginatedResponse[UserResponse]:
    """
    Get paginated list of all users.
    
    Args:
        pagination: Pagination parameters
        user_service: User service instance
        current_user: Authenticated user with permission
        search: Optional search term
        
    Returns:
        PaginatedResponse: Paginated user list
    """
    users, total = await user_service.get_users(
        skip=pagination.offset,
        limit=pagination.limit,
        search=search
    )
    
    return PaginatedResponse.create(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User",
    description="Create a new user. Admin only."
)
async def create_user(
    user_data: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_admin_user)]
) -> UserResponse:
    """
    Create a new user (admin only).
    
    Args:
        user_data: User creation data
        user_service: User service instance
        current_user: Admin user
        
    Returns:
        UserResponse: Created user
    """
    user = await user_service.create_user(user_data)
    logger.info("User created by admin", 
                admin_id=current_user.id, 
                new_user_id=user.id)
    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get User",
    description="Get a specific user by ID."
)
async def get_user(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> UserResponse:
    """
    Get a user by ID.
    
    Regular users can only view their own profile.
    Admins and managers can view any user.
    
    Args:
        user_id: The user ID to retrieve
        user_service: User service instance
        current_user: Authenticated user
        
    Returns:
        UserResponse: User details
    """
    # Check permission for viewing other users
    if user_id != current_user.id and not current_user.has_permission("users:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile"
        )
    
    user = await user_service.get_user(user_id)
    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update User",
    description="Update a user's information."
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> UserResponse:
    """
    Update a user's information.
    
    Regular users can update their own profile (except role).
    Admins can update any user including role.
    
    Args:
        user_id: The user ID to update
        user_data: Update data
        user_service: User service instance
        current_user: Authenticated user
        
    Returns:
        UserResponse: Updated user
    """
    # Check permission for updating other users
    if user_id != current_user.id:
        if not current_user.has_permission("users:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own profile"
            )
    
    # Only admins can change roles
    if user_data.role is not None and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change user roles"
        )
    
    user = await user_service.update_user(user_id, user_data)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete User",
    description="Delete a user (soft delete). Admin only."
)
async def delete_user(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_admin_user)]
) -> MessageResponse:
    """
    Soft delete a user (admin only).
    
    Args:
        user_id: The user ID to delete
        user_service: User service instance
        current_user: Admin user
        
    Returns:
        MessageResponse: Deletion confirmation
    """
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )
    
    await user_service.delete_user(user_id)
    
    return MessageResponse(
        message=f"User {user_id} has been deleted",
        success=True
    )


@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activate User",
    description="Activate a deactivated user account. Admin only."
)
async def activate_user(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_admin_user)]
) -> UserResponse:
    """
    Activate a user account.
    
    Args:
        user_id: The user ID to activate
        user_service: User service instance
        current_user: Admin user
        
    Returns:
        UserResponse: Updated user
    """
    from app.schemas.user import UserUpdate
    
    user = await user_service.update_user(
        user_id,
        UserUpdate(is_active=True)
    )
    
    logger.info("User activated", user_id=user_id, admin_id=current_user.id)
    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Deactivate User",
    description="Deactivate a user account. Admin only."
)
async def deactivate_user(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_admin_user)]
) -> UserResponse:
    """
    Deactivate a user account.
    
    Args:
        user_id: The user ID to deactivate
        user_service: User service instance
        current_user: Admin user
        
    Returns:
        UserResponse: Updated user
    """
    from app.schemas.user import UserUpdate
    
    # Prevent self-deactivation
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account"
        )
    
    user = await user_service.update_user(
        user_id,
        UserUpdate(is_active=False)
    )
    
    logger.info("User deactivated", user_id=user_id, admin_id=current_user.id)
    return UserResponse.model_validate(user)
