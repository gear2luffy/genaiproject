"""
Authentication endpoints.

Demonstrates:
- OAuth2 password flow
- JWT token generation
- Token refresh
- Login/logout handling
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user import (
    Token,
    UserCreate,
    UserResponse,
    UserLogin,
    RefreshTokenRequest,
    PasswordChange,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.dependencies.auth import get_current_active_user
from app.dependencies.services import get_auth_service, get_user_service
from app.models.user import User
from app.core.exceptions import AuthenticationError
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Create a new user account. Email must be unique."
)
async def register(
    user_data: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
    background_tasks: BackgroundTasks
) -> UserResponse:
    """
    Register a new user account.
    
    Args:
        user_data: User registration data
        user_service: User service instance
        background_tasks: Background task queue
        
    Returns:
        UserResponse: Created user information
        
    Raises:
        HTTPException: If email or username already exists
    """
    user = await user_service.create_user(user_data)
    
    # Add background task for sending welcome email
    background_tasks.add_task(
        send_welcome_email,
        user.email,
        user.full_name or user.username
    )
    
    logger.info("New user registered", user_id=user.id)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="User Login",
    description="Authenticate user and return JWT tokens."
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    """
    Authenticate user with email/password and return tokens.
    
    This endpoint follows OAuth2 password flow specification.
    The username field should contain the user's email.
    
    Args:
        form_data: OAuth2 form with username (email) and password
        auth_service: Authentication service
        
    Returns:
        Token: Access and refresh tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Note: OAuth2 spec uses 'username' but we use email
        credentials = UserLogin(
            email=form_data.username,
            password=form_data.password
        )
        token = await auth_service.login(credentials)
        return token
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post(
    "/login/json",
    response_model=Token,
    summary="User Login (JSON)",
    description="Authenticate user with JSON body and return JWT tokens."
)
async def login_json(
    credentials: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    """
    Authenticate user with JSON credentials.
    
    Alternative login endpoint accepting JSON body instead of
    form data for easier API consumption.
    
    Args:
        credentials: Login credentials (email and password)
        auth_service: Authentication service
        
    Returns:
        Token: Access and refresh tokens
    """
    try:
        return await auth_service.login(credentials)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh Access Token",
    description="Get new access token using refresh token."
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    """
    Refresh access token using a valid refresh token.
    
    Args:
        request: Refresh token request body
        auth_service: Authentication service
        
    Returns:
        Token: New access and refresh tokens
    """
    try:
        return await auth_service.refresh_access_token(request.refresh_token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message)
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    description="Get the currently authenticated user's profile."
)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> UserResponse:
    """
    Get current authenticated user's profile.
    
    Args:
        current_user: Authenticated user from token
        
    Returns:
        UserResponse: Current user's profile
    """
    return UserResponse.model_validate(current_user)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change Password",
    description="Change the current user's password."
)
async def change_password(
    password_data: PasswordChange,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> MessageResponse:
    """
    Change current user's password.
    
    Args:
        password_data: Current and new password
        current_user: Authenticated user
        user_service: User service instance
        
    Returns:
        MessageResponse: Success message
    """
    await user_service.change_password(
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    return MessageResponse(
        message="Password changed successfully",
        success=True
    )


# Background task functions
async def send_welcome_email(email: str, name: str) -> None:
    """
    Send welcome email to new user (placeholder).
    
    In production, this would integrate with an email service.
    
    Args:
        email: User's email address
        name: User's name
    """
    logger.info(
        "Sending welcome email",
        email=email,
        name=name
    )
    # Email sending logic would go here
