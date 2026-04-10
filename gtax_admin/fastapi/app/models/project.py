"""
Project model for organizing tasks.

Demonstrates:
- Parent-child relationships
- Enum for status management
- Computed properties
- Query optimization with indexes
"""

import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.base import BaseModelMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task


class ProjectStatus(str, enum.Enum):
    """Enumeration of project statuses."""
    
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base, BaseModelMixin, SoftDeleteMixin):
    """
    Project model for organizing and grouping tasks.
    
    Demonstrates:
    - Foreign key relationships
    - Cascade delete behavior
    - Status transitions
    - Computed properties for analytics
    """
    
    __tablename__ = "projects"
    
    # Primary key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        doc="Unique project identifier"
    )
    
    # Project details
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        doc="Project name"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Project description"
    )
    
    slug: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
        index=True,
        doc="URL-friendly project identifier"
    )
    
    # Project status
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus),
        default=ProjectStatus.PLANNING,
        nullable=False,
        doc="Current project status"
    )
    
    # Ownership
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID of the project owner"
    )
    
    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="projects",
        lazy="joined"
    )
    
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="project",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    # Table-level configurations
    __table_args__ = (
        Index("ix_projects_owner_status", "owner_id", "status"),
        Index("ix_projects_status", "status"),
        {"comment": "Projects table for organizing tasks"}
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Project(id={self.id}, name='{self.name}', status={self.status})>"
    
    @property
    def task_count(self) -> int:
        """Get the total number of tasks in the project."""
        return len(self.tasks) if self.tasks else 0
    
    @property
    def completed_task_count(self) -> int:
        """Get the number of completed tasks."""
        if not self.tasks:
            return 0
        return sum(1 for task in self.tasks if task.status.value == "completed")
    
    @property
    def completion_percentage(self) -> float:
        """Calculate the project completion percentage."""
        if not self.tasks:
            return 0.0
        return (self.completed_task_count / self.task_count) * 100
    
    def activate(self) -> None:
        """Transition project to active status."""
        if self.status in [ProjectStatus.PLANNING, ProjectStatus.ON_HOLD]:
            self.status = ProjectStatus.ACTIVE
    
    def complete(self) -> None:
        """Mark project as completed."""
        self.status = ProjectStatus.COMPLETED
    
    def archive(self) -> None:
        """Archive the project."""
        self.status = ProjectStatus.ARCHIVED
    
    def put_on_hold(self) -> None:
        """Put project on hold."""
        if self.status == ProjectStatus.ACTIVE:
            self.status = ProjectStatus.ON_HOLD
