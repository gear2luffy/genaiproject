"""
Task model for tracking work items.

Demonstrates:
- Multiple foreign key relationships
- Enum fields for status and priority
- Date/time handling
- Business logic methods
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.base import BaseModelMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project


class TaskStatus(str, enum.Enum):
    """Enumeration of task statuses."""
    
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """Enumeration of task priorities."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(Base, BaseModelMixin, SoftDeleteMixin):
    """
    Task model for tracking work items.
    
    Demonstrates:
    - Complex relationships with multiple foreign keys
    - Status and priority management
    - Due date handling
    - Workflow transitions
    """
    
    __tablename__ = "tasks"
    
    # Primary key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        doc="Unique task identifier"
    )
    
    # Task details
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        doc="Task title"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Detailed task description"
    )
    
    # Status and priority
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        default=TaskStatus.TODO,
        nullable=False,
        index=True,
        doc="Current task status"
    )
    
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority),
        default=TaskPriority.MEDIUM,
        nullable=False,
        index=True,
        doc="Task priority level"
    )
    
    # Dates
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        doc="Task due date"
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the task was completed"
    )
    
    # Relationships - Project
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID of the parent project"
    )
    
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="tasks",
        lazy="joined"
    )
    
    # Relationships - Assignee
    assignee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="ID of the assigned user"
    )
    
    assignee: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="assigned_tasks",
        lazy="joined",
        foreign_keys=[assignee_id]
    )
    
    # Relationships - Creator
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID of the user who created the task"
    )
    
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_tasks",
        lazy="joined",
        foreign_keys=[created_by]
    )
    
    # Table-level configurations
    __table_args__ = (
        Index("ix_tasks_project_status", "project_id", "status"),
        Index("ix_tasks_assignee_status", "assignee_id", "status"),
        Index("ix_tasks_due_date", "due_date"),
        Index("ix_tasks_priority_status", "priority", "status"),
        {"comment": "Tasks table for tracking work items"}
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Task(id={self.id}, title='{self.title}', status={self.status})>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if the task is overdue."""
        if self.due_date is None:
            return False
        if self.status == TaskStatus.COMPLETED:
            return False
        return datetime.utcnow() > self.due_date.replace(tzinfo=None)
    
    @property
    def is_assigned(self) -> bool:
        """Check if the task is assigned to someone."""
        return self.assignee_id is not None
    
    @property
    def is_completed(self) -> bool:
        """Check if the task is completed."""
        return self.status == TaskStatus.COMPLETED
    
    def start(self) -> None:
        """Start working on the task."""
        if self.status == TaskStatus.TODO:
            self.status = TaskStatus.IN_PROGRESS
    
    def submit_for_review(self) -> None:
        """Submit the task for review."""
        if self.status == TaskStatus.IN_PROGRESS:
            self.status = TaskStatus.IN_REVIEW
    
    def complete(self) -> None:
        """Mark the task as completed."""
        if self.status in [TaskStatus.IN_PROGRESS, TaskStatus.IN_REVIEW]:
            self.status = TaskStatus.COMPLETED
            self.completed_at = datetime.utcnow()
    
    def block(self) -> None:
        """Block the task."""
        self.status = TaskStatus.BLOCKED
    
    def unblock(self) -> None:
        """Unblock the task and return to in-progress."""
        if self.status == TaskStatus.BLOCKED:
            self.status = TaskStatus.IN_PROGRESS
    
    def cancel(self) -> None:
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED
    
    def assign_to(self, user_id: int) -> None:
        """
        Assign the task to a user.
        
        Args:
            user_id: The ID of the user to assign
        """
        self.assignee_id = user_id
    
    def unassign(self) -> None:
        """Remove the task assignment."""
        self.assignee_id = None
