"""
Project management endpoints.

Demonstrates:
- CRUD operations with authorization
- Nested resource access (project tasks)
- Filtering and sorting
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectFilter,
)
from app.schemas.common import MessageResponse, PaginatedResponse
from app.models.project import ProjectStatus
from app.models.user import User
from app.services.project_service import ProjectService
from app.dependencies.auth import get_current_active_user
from app.dependencies.services import get_project_service
from app.dependencies.pagination import get_pagination, PaginationParams
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[ProjectResponse],
    summary="List Projects",
    description="Get paginated list of projects with filtering options."
)
async def list_projects(
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    status: Annotated[
        Optional[ProjectStatus],
        Query(description="Filter by project status")
    ] = None,
    owner_id: Annotated[
        Optional[int],
        Query(description="Filter by owner ID")
    ] = None,
    search: Annotated[
        Optional[str],
        Query(description="Search in name and description")
    ] = None,
    my_projects: Annotated[
        bool,
        Query(description="Show only my projects")
    ] = False
) -> PaginatedResponse[ProjectResponse]:
    """
    Get paginated list of projects.
    
    Args:
        pagination: Pagination parameters
        project_service: Project service instance
        current_user: Authenticated user
        status: Optional status filter
        owner_id: Optional owner filter
        search: Optional search term
        my_projects: If true, show only current user's projects
        
    Returns:
        PaginatedResponse: Paginated project list
    """
    # If my_projects flag is set, filter by current user
    if my_projects:
        owner_id = current_user.id
    
    projects, total = await project_service.get_projects(
        skip=pagination.offset,
        limit=pagination.limit,
        search=search,
        status=status,
        owner_id=owner_id
    )
    
    return PaginatedResponse.create(
        items=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Project",
    description="Create a new project. The current user becomes the owner."
)
async def create_project(
    project_data: ProjectCreate,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> ProjectResponse:
    """
    Create a new project.
    
    Args:
        project_data: Project creation data
        project_service: Project service instance
        current_user: Authenticated user (becomes owner)
        
    Returns:
        ProjectResponse: Created project
    """
    project = await project_service.create_project(
        project_data=project_data,
        owner_id=current_user.id
    )
    
    return ProjectResponse.model_validate(project)


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Get Project",
    description="Get a specific project by ID with full details."
)
async def get_project(
    project_id: int,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> ProjectDetailResponse:
    """
    Get project details by ID.
    
    Args:
        project_id: The project ID
        project_service: Project service instance
        current_user: Authenticated user
        
    Returns:
        ProjectDetailResponse: Project with full details
    """
    project = await project_service.get_project(project_id)
    
    # Build response with computed fields
    response = ProjectDetailResponse.model_validate(project)
    response.task_count = project.task_count
    response.completed_task_count = project.completed_task_count
    response.completion_percentage = project.completion_percentage
    
    return response


@router.get(
    "/slug/{slug}",
    response_model=ProjectDetailResponse,
    summary="Get Project by Slug",
    description="Get a specific project by URL slug."
)
async def get_project_by_slug(
    slug: str,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> ProjectDetailResponse:
    """
    Get project by URL slug.
    
    Args:
        slug: The project slug
        project_service: Project service instance
        current_user: Authenticated user
        
    Returns:
        ProjectDetailResponse: Project with full details
    """
    project = await project_service.get_project_by_slug(slug)
    
    response = ProjectDetailResponse.model_validate(project)
    response.task_count = project.task_count
    response.completed_task_count = project.completed_task_count
    response.completion_percentage = project.completion_percentage
    
    return response


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update Project",
    description="Update a project's information. Only owner or admin can update."
)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> ProjectResponse:
    """
    Update project details.
    
    Args:
        project_id: The project ID
        project_data: Update data
        project_service: Project service instance
        current_user: Authenticated user
        
    Returns:
        ProjectResponse: Updated project
    """
    project = await project_service.update_project(
        project_id=project_id,
        project_data=project_data,
        current_user=current_user
    )
    
    return ProjectResponse.model_validate(project)


@router.delete(
    "/{project_id}",
    response_model=MessageResponse,
    summary="Delete Project",
    description="Delete a project (soft delete). Only owner or admin can delete."
)
async def delete_project(
    project_id: int,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> MessageResponse:
    """
    Delete a project.
    
    Args:
        project_id: The project ID
        project_service: Project service instance
        current_user: Authenticated user
        
    Returns:
        MessageResponse: Deletion confirmation
    """
    await project_service.delete_project(
        project_id=project_id,
        current_user=current_user
    )
    
    return MessageResponse(
        message=f"Project {project_id} has been deleted",
        success=True
    )


@router.patch(
    "/{project_id}/status",
    response_model=ProjectResponse,
    summary="Change Project Status",
    description="Change the status of a project."
)
async def change_project_status(
    project_id: int,
    status: ProjectStatus,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> ProjectResponse:
    """
    Change project status.
    
    Args:
        project_id: The project ID
        status: New project status
        project_service: Project service instance
        current_user: Authenticated user
        
    Returns:
        ProjectResponse: Updated project
    """
    project = await project_service.change_project_status(
        project_id=project_id,
        new_status=status,
        current_user=current_user
    )
    
    return ProjectResponse.model_validate(project)


@router.post(
    "/{project_id}/archive",
    response_model=ProjectResponse,
    summary="Archive Project",
    description="Archive a project."
)
async def archive_project(
    project_id: int,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> ProjectResponse:
    """
    Archive a project.
    
    Args:
        project_id: The project ID
        project_service: Project service instance
        current_user: Authenticated user
        
    Returns:
        ProjectResponse: Archived project
    """
    project = await project_service.change_project_status(
        project_id=project_id,
        new_status=ProjectStatus.ARCHIVED,
        current_user=current_user
    )
    
    return ProjectResponse.model_validate(project)
