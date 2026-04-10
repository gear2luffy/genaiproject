"""Pydantic schemas for request/response validation."""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserInDB,
    UserLogin,
    Token,
    TokenPayload,
)
from app.schemas.project import (
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.schemas.task import (
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)
from app.schemas.common import (
    PaginationParams,
    PaginatedResponse,
    MessageResponse,
    HealthResponse,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    "UserLogin",
    "Token",
    "TokenPayload",
    # Project schemas
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectListResponse",
    # Task schemas
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    # Common schemas
    "PaginationParams",
    "PaginatedResponse",
    "MessageResponse",
    "HealthResponse",
]
