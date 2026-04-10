"""
Task-related Pydantic schemas.

Demonstrates:
- Complex nested models
- Multiple relationship schemas
- Time-based validation
"""

from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.models.task import TaskPriority, TaskStatus
from app.schemas.common import BaseSchema


class TaskBase(BaseSchema):
    """Base task schema with shared fields."""
    
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title",
        examples=["Implement user authentication"]
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Detailed task description"
    )


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    
    project_id: int = Field(
        description="ID of the parent project",
        gt=0
    )
    status: TaskStatus = Field(
        default=TaskStatus.TODO,
        description="Initial task status"
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Task priority level"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Task due date"
    )
    assignee_id: Optional[int] = Field(
        default=None,
        description="ID of the assigned user",
        gt=0
    )
    
    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Ensure due date is in the future."""
        if v is not None and v < datetime.utcnow():
            raise ValueError("Due date must be in the future")
        return v


class TaskUpdate(BaseSchema):
    """Schema for updating a task."""
    
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="New task title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="New task description"
    )
    status: Optional[TaskStatus] = Field(
        default=None,
        description="New task status"
    )
    priority: Optional[TaskPriority] = Field(
        default=None,
        description="New task priority"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="New due date"
    )
    assignee_id: Optional[int] = Field(
        default=None,
        description="New assignee ID"
    )


class TaskAssign(BaseSchema):
    """Schema for assigning a task to a user."""
    
    assignee_id: int = Field(
        description="ID of the user to assign",
        gt=0
    )


class TaskStatusUpdate(BaseSchema):
    """Schema for updating only task status."""
    
    status: TaskStatus = Field(description="New task status")


class UserSummary(BaseSchema):
    """Nested schema for user summary in task response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    full_name: Optional[str] = None


class ProjectSummary(BaseSchema):
    """Nested schema for project summary in task response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    slug: str
    status: str


class TaskResponse(TaskBase):
    """Schema for task response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(description="Task ID")
    project_id: int = Field(description="Parent project ID")
    status: TaskStatus = Field(description="Task status")
    priority: TaskPriority = Field(description="Task priority")
    due_date: Optional[datetime] = Field(description="Task due date")
    completed_at: Optional[datetime] = Field(description="Completion timestamp")
    assignee_id: Optional[int] = Field(description="Assignee user ID")
    created_by: int = Field(description="Creator user ID")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    # Nested relationships
    assignee: Optional[UserSummary] = Field(
        default=None,
        description="Assigned user details"
    )
    creator: Optional[UserSummary] = Field(
        default=None,
        description="Task creator details"
    )
    project: Optional[ProjectSummary] = Field(
        default=None,
        description="Parent project details"
    )
    
    # Computed fields
    is_overdue: bool = Field(
        default=False,
        description="Whether the task is overdue"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Implement user authentication",
                "description": "Add JWT-based auth with refresh tokens",
                "project_id": 1,
                "status": "in_progress",
                "priority": "high",
                "due_date": "2025-02-01T00:00:00Z",
                "completed_at": None,
                "assignee_id": 2,
                "created_by": 1,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-15T00:00:00Z",
                "is_overdue": False,
                "assignee": {
                    "id": 2,
                    "username": "jane_doe",
                    "email": "jane@example.com",
                    "full_name": "Jane Doe"
                },
                "creator": {
                    "id": 1,
                    "username": "john_doe",
                    "email": "john@example.com",
                    "full_name": "John Doe"
                },
                "project": {
                    "id": 1,
                    "name": "My Project",
                    "slug": "my-project",
                    "status": "active"
                }
            }
        }


class TaskListResponse(BaseSchema):
    """Schema for paginated task list response."""
    
    items: List[TaskResponse]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool


class TaskFilter(BaseSchema):
    """Filter parameters for task list."""
    
    project_id: Optional[int] = Field(
        default=None,
        description="Filter by project ID"
    )
    status: Optional[TaskStatus] = Field(
        default=None,
        description="Filter by status"
    )
    priority: Optional[TaskPriority] = Field(
        default=None,
        description="Filter by priority"
    )
    assignee_id: Optional[int] = Field(
        default=None,
        description="Filter by assignee ID"
    )
    created_by: Optional[int] = Field(
        default=None,
        description="Filter by creator ID"
    )
    is_overdue: Optional[bool] = Field(
        default=None,
        description="Filter overdue tasks"
    )
    search: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Search in title and description"
    )
    due_before: Optional[datetime] = Field(
        default=None,
        description="Filter tasks due before this date"
    )
    due_after: Optional[datetime] = Field(
        default=None,
        description="Filter tasks due after this date"
    )


class TaskBulkUpdate(BaseSchema):
    """Schema for bulk task updates."""
    
    task_ids: List[int] = Field(
        min_length=1,
        max_length=100,
        description="List of task IDs to update"
    )
    status: Optional[TaskStatus] = Field(
        default=None,
        description="New status for all tasks"
    )
    priority: Optional[TaskPriority] = Field(
        default=None,
        description="New priority for all tasks"
    )
    assignee_id: Optional[int] = Field(
        default=None,
        description="New assignee for all tasks"
    )
    
    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "TaskBulkUpdate":
        """Ensure at least one update field is provided."""
        if not any([self.status, self.priority, self.assignee_id]):
            raise ValueError("At least one update field must be provided")
        return self
