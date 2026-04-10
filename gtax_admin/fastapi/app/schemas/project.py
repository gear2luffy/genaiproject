"""
Project-related Pydantic schemas.

Demonstrates:
- Nested models with relationships
- Computed fields
- Slug generation
"""

from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict, Field, field_validator, computed_field

from app.models.project import ProjectStatus
from app.schemas.common import BaseSchema


class ProjectBase(BaseSchema):
    """Base project schema with shared fields."""
    
    name: str = Field(
        min_length=1,
        max_length=200,
        description="Project name",
        examples=["My Awesome Project"]
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Project description",
        examples=["A project for managing tasks efficiently"]
    )


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    
    status: ProjectStatus = Field(
        default=ProjectStatus.PLANNING,
        description="Initial project status"
    )
    slug: Optional[str] = Field(
        default=None,
        max_length=200,
        pattern=r"^[a-z0-9-]+$",
        description="URL-friendly slug (auto-generated if not provided)"
    )
    
    @field_validator("slug", mode="before")
    @classmethod
    def generate_slug(cls, v: Optional[str], info) -> str:
        """Generate slug from name if not provided."""
        if v:
            return v.lower().strip()
        # Access the name field from the data
        name = info.data.get("name", "")
        if name:
            # Generate slug from name
            import re
            slug = name.lower()
            slug = re.sub(r"[^\w\s-]", "", slug)
            slug = re.sub(r"[\s_]+", "-", slug)
            slug = re.sub(r"-+", "-", slug)
            return slug.strip("-")
        return ""


class ProjectUpdate(BaseSchema):
    """Schema for updating a project."""
    
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="New project name"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="New project description"
    )
    status: Optional[ProjectStatus] = Field(
        default=None,
        description="New project status"
    )


class ProjectOwner(BaseSchema):
    """Nested schema for project owner information."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    full_name: Optional[str] = None


class TaskSummary(BaseSchema):
    """Nested schema for task summary in project response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    status: str
    priority: str


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(description="Project ID")
    slug: str = Field(description="URL-friendly slug")
    status: ProjectStatus = Field(description="Project status")
    owner_id: int = Field(description="Owner user ID")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    # Nested relationships (optional loading)
    owner: Optional[ProjectOwner] = Field(
        default=None,
        description="Project owner details"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "My Awesome Project",
                "description": "A project for managing tasks efficiently",
                "slug": "my-awesome-project",
                "status": "active",
                "owner_id": 1,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "owner": {
                    "id": 1,
                    "username": "john_doe",
                    "email": "john@example.com",
                    "full_name": "John Doe"
                }
            }
        }


class ProjectDetailResponse(ProjectResponse):
    """
    Detailed project response with task information.
    
    Used when fetching a single project with full details.
    """
    
    tasks: List[TaskSummary] = Field(
        default_factory=list,
        description="List of tasks in the project"
    )
    task_count: int = Field(
        default=0,
        description="Total number of tasks"
    )
    completed_task_count: int = Field(
        default=0,
        description="Number of completed tasks"
    )
    completion_percentage: float = Field(
        default=0.0,
        description="Project completion percentage"
    )


class ProjectListResponse(BaseSchema):
    """Schema for paginated project list response."""
    
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool


class ProjectFilter(BaseSchema):
    """Filter parameters for project list."""
    
    status: Optional[ProjectStatus] = Field(
        default=None,
        description="Filter by status"
    )
    owner_id: Optional[int] = Field(
        default=None,
        description="Filter by owner ID"
    )
    search: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Search in name and description"
    )
