"""
Task management endpoints.

Demonstrates:
- Complex filtering and sorting
- Bulk operations
- Status transitions
- Nested resource handling
"""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskFilter,
    TaskAssign,
    TaskStatusUpdate,
    TaskBulkUpdate,
)
from app.schemas.common import MessageResponse, PaginatedResponse
from app.models.task import TaskStatus, TaskPriority
from app.models.user import User
from app.services.task_service import TaskService
from app.dependencies.auth import get_current_active_user
from app.dependencies.services import get_task_service
from app.dependencies.pagination import get_pagination, PaginationParams
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[TaskResponse],
    summary="List Tasks",
    description="Get paginated list of tasks with comprehensive filtering options."
)
async def list_tasks(
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_id: Annotated[Optional[int], Query(description="Filter by project")] = None,
    status: Annotated[Optional[TaskStatus], Query(description="Filter by status")] = None,
    priority: Annotated[Optional[TaskPriority], Query(description="Filter by priority")] = None,
    assignee_id: Annotated[Optional[int], Query(description="Filter by assignee")] = None,
    search: Annotated[Optional[str], Query(description="Search in title/description")] = None,
    is_overdue: Annotated[Optional[bool], Query(description="Filter overdue tasks")] = None,
    my_tasks: Annotated[bool, Query(description="Show only my assigned tasks")] = False
) -> PaginatedResponse[TaskResponse]:
    """
    Get paginated list of tasks with filtering.
    
    Args:
        pagination: Pagination parameters
        task_service: Task service instance
        current_user: Authenticated user
        project_id: Filter by project
        status: Filter by status
        priority: Filter by priority
        assignee_id: Filter by assignee
        search: Search term
        is_overdue: Filter overdue tasks
        my_tasks: Show only current user's assigned tasks
        
    Returns:
        PaginatedResponse: Paginated task list
    """
    # Build filters
    filters = TaskFilter(
        project_id=project_id,
        status=status,
        priority=priority,
        assignee_id=assignee_id if not my_tasks else current_user.id,
        search=search,
        is_overdue=is_overdue
    )
    
    tasks, total = await task_service.get_tasks(
        filters=filters,
        skip=pagination.offset,
        limit=pagination.limit,
        sort_by=pagination.sort_by or "created_at",
        sort_order=pagination.sort_order
    )
    
    # Convert to response models with computed fields
    task_responses = []
    for task in tasks:
        response = TaskResponse.model_validate(task)
        response.is_overdue = task.is_overdue
        task_responses.append(response)
    
    return PaginatedResponse.create(
        items=task_responses,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Task",
    description="Create a new task in a project."
)
async def create_task(
    task_data: TaskCreate,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    background_tasks: BackgroundTasks
) -> TaskResponse:
    """
    Create a new task.
    
    Args:
        task_data: Task creation data
        task_service: Task service instance
        current_user: Authenticated user (becomes creator)
        background_tasks: Background task queue
        
    Returns:
        TaskResponse: Created task
    """
    task = await task_service.create_task(
        task_data=task_data,
        created_by=current_user.id
    )
    
    # Add background task for notifications
    if task.assignee_id:
        background_tasks.add_task(
            notify_task_assigned,
            task.id,
            task.assignee_id
        )
    
    response = TaskResponse.model_validate(task)
    response.is_overdue = task.is_overdue
    return response


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get Task",
    description="Get a specific task by ID."
)
async def get_task(
    task_id: int,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> TaskResponse:
    """
    Get task details by ID.
    
    Args:
        task_id: The task ID
        task_service: Task service instance
        current_user: Authenticated user
        
    Returns:
        TaskResponse: Task details
    """
    task = await task_service.get_task(task_id)
    
    response = TaskResponse.model_validate(task)
    response.is_overdue = task.is_overdue
    return response


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update Task",
    description="Update a task's information."
)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> TaskResponse:
    """
    Update task details.
    
    Args:
        task_id: The task ID
        task_data: Update data
        task_service: Task service instance
        current_user: Authenticated user
        
    Returns:
        TaskResponse: Updated task
    """
    task = await task_service.update_task(
        task_id=task_id,
        task_data=task_data,
        current_user=current_user
    )
    
    response = TaskResponse.model_validate(task)
    response.is_overdue = task.is_overdue
    return response


@router.delete(
    "/{task_id}",
    response_model=MessageResponse,
    summary="Delete Task",
    description="Delete a task (soft delete)."
)
async def delete_task(
    task_id: int,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> MessageResponse:
    """
    Delete a task.
    
    Args:
        task_id: The task ID
        task_service: Task service instance
        current_user: Authenticated user
        
    Returns:
        MessageResponse: Deletion confirmation
    """
    await task_service.delete_task(
        task_id=task_id,
        current_user=current_user
    )
    
    return MessageResponse(
        message=f"Task {task_id} has been deleted",
        success=True
    )


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="Change Task Status",
    description="Change the status of a task with transition validation."
)
async def change_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> TaskResponse:
    """
    Change task status.
    
    Validates that the status transition is allowed.
    
    Args:
        task_id: The task ID
        status_update: New status
        task_service: Task service instance
        current_user: Authenticated user
        
    Returns:
        TaskResponse: Updated task
    """
    task = await task_service.change_task_status(
        task_id=task_id,
        new_status=status_update.status,
        current_user=current_user
    )
    
    response = TaskResponse.model_validate(task)
    response.is_overdue = task.is_overdue
    return response


@router.patch(
    "/{task_id}/assign",
    response_model=TaskResponse,
    summary="Assign Task",
    description="Assign a task to a user."
)
async def assign_task(
    task_id: int,
    assignment: TaskAssign,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    background_tasks: BackgroundTasks
) -> TaskResponse:
    """
    Assign task to a user.
    
    Args:
        task_id: The task ID
        assignment: Assignment data with assignee ID
        task_service: Task service instance
        current_user: Authenticated user
        background_tasks: Background task queue
        
    Returns:
        TaskResponse: Updated task
    """
    task = await task_service.assign_task(
        task_id=task_id,
        assignee_id=assignment.assignee_id,
        current_user=current_user
    )
    
    # Notify assignee
    background_tasks.add_task(
        notify_task_assigned,
        task.id,
        assignment.assignee_id
    )
    
    response = TaskResponse.model_validate(task)
    response.is_overdue = task.is_overdue
    return response


@router.patch(
    "/{task_id}/unassign",
    response_model=TaskResponse,
    summary="Unassign Task",
    description="Remove task assignment."
)
async def unassign_task(
    task_id: int,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> TaskResponse:
    """
    Remove task assignment.
    
    Args:
        task_id: The task ID
        task_service: Task service instance
        current_user: Authenticated user
        
    Returns:
        TaskResponse: Updated task
    """
    task = await task_service.unassign_task(
        task_id=task_id,
        current_user=current_user
    )
    
    response = TaskResponse.model_validate(task)
    response.is_overdue = task.is_overdue
    return response


@router.post(
    "/bulk/update",
    response_model=MessageResponse,
    summary="Bulk Update Tasks",
    description="Update multiple tasks at once."
)
async def bulk_update_tasks(
    bulk_data: TaskBulkUpdate,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> MessageResponse:
    """
    Bulk update multiple tasks.
    
    Args:
        bulk_data: Bulk update data with task IDs and new values
        task_service: Task service instance
        current_user: Authenticated user
        
    Returns:
        MessageResponse: Update results
    """
    updated_count = 0
    
    if bulk_data.status:
        updated_count = await task_service.bulk_update_status(
            task_ids=bulk_data.task_ids,
            new_status=bulk_data.status,
            current_user=current_user
        )
    
    return MessageResponse(
        message=f"Updated {updated_count} of {len(bulk_data.task_ids)} tasks",
        success=True,
        data={"updated_count": updated_count}
    )


@router.get(
    "/project/{project_id}",
    response_model=List[TaskResponse],
    summary="Get Project Tasks",
    description="Get all tasks for a specific project."
)
async def get_project_tasks(
    project_id: int,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> List[TaskResponse]:
    """
    Get all tasks for a project.
    
    Args:
        project_id: The project ID
        task_service: Task service instance
        current_user: Authenticated user
        
    Returns:
        List[TaskResponse]: Project tasks
    """
    tasks = await task_service.get_project_tasks(project_id)
    
    return [
        TaskResponse.model_validate(task)
        for task in tasks
    ]


@router.get(
    "/statistics",
    summary="Get Task Statistics",
    description="Get task statistics and counts."
)
async def get_task_statistics(
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_id: Annotated[Optional[int], Query(description="Filter by project")] = None
) -> dict:
    """
    Get task statistics.
    
    Args:
        task_service: Task service instance
        current_user: Authenticated user
        project_id: Optional project filter
        
    Returns:
        dict: Task statistics
    """
    return await task_service.get_task_statistics(project_id)


# Background task functions
async def notify_task_assigned(task_id: int, assignee_id: int) -> None:
    """
    Send notification when task is assigned (placeholder).
    
    Args:
        task_id: The task ID
        assignee_id: The assigned user's ID
    """
    logger.info(
        "Task assignment notification",
        task_id=task_id,
        assignee_id=assignee_id
    )
    # Notification logic would go here
