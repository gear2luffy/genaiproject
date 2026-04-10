"""Dependencies module for FastAPI dependency injection."""

from app.dependencies.auth import (
    get_current_user,
    get_current_active_user,
    get_admin_user,
    get_manager_or_admin_user,
    require_permission,
)
from app.dependencies.pagination import PaginationDep
from app.dependencies.services import (
    get_user_service,
    get_project_service,
    get_task_service,
    get_auth_service,
)

__all__ = [
    # Auth dependencies
    "get_current_user",
    "get_current_active_user",
    "get_admin_user",
    "get_manager_or_admin_user",
    "require_permission",
    # Pagination
    "PaginationDep",
    # Services
    "get_user_service",
    "get_project_service",
    "get_task_service",
    "get_auth_service",
]
