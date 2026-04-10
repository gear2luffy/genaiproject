"""
User model for authentication and authorization.

Demonstrates:
- SQLAlchemy 2.0 ORM model definition
- Enum fields for roles
- Relationship definitions
- Password hashing integration
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.base import BaseModelMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.task import Task


class UserRole(str, enum.Enum):
    """
    Enumeration of user roles for authorization.
    
    Demonstrates:
    - Enum inheritance from str for JSON serialization
    - Role-based access control levels
    """
    
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    
    @classmethod
    def get_permissions(cls, role: "UserRole") -> List[str]:
        """
        Get permissions for a role.
        
        Args:
            role: The user role
            
        Returns:
            List[str]: List of permission strings
        """
        permissions_map = {
            cls.ADMIN: [
                "users:read", "users:write", "users:delete",
                "projects:read", "projects:write", "projects:delete",
                "tasks:read", "tasks:write", "tasks:delete",
                "admin:access"
            ],
            cls.MANAGER: [
                "users:read",
                "projects:read", "projects:write",
                "tasks:read", "tasks:write", "tasks:delete"
            ],
            cls.USER: [
                "projects:read",
                "tasks:read", "tasks:write"
            ]
        }
        return permissions_map.get(role, [])


class User(Base, BaseModelMixin, SoftDeleteMixin):
    """
    User model for authentication and authorization.
    
    Demonstrates:
    - Complete SQLAlchemy model definition
    - Multiple mixins for shared functionality
    - Relationships with lazy loading
    - Database indexes for performance
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        doc="Unique user identifier"
    )
    
    # User credentials
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="User email address (unique)"
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Bcrypt hashed password"
    )
    
    # User profile
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Unique username"
    )
    
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="User's full name"
    )
    
    # User status and role
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False,
        doc="User role for authorization"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether the user account is active"
    )
    
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the user email is verified"
    )
    
    # Metadata
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        doc="Last login timestamp"
    )
    
    # Relationships
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="owner",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    assigned_tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="assignee",
        lazy="selectin",
        foreign_keys="Task.assignee_id"
    )
    
    created_tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="creator",
        lazy="selectin",
        foreign_keys="Task.created_by"
    )
    
    # Table-level configurations
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
        Index("ix_users_role", "role"),
        {"comment": "Users table for authentication and authorization"}
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User(id={self.id}, email='{self.email}', role={self.role})>"
    
    @property
    def permissions(self) -> List[str]:
        """Get user's permissions based on role."""
        return UserRole.get_permissions(self.role)
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            permission: The permission to check
            
        Returns:
            bool: True if user has the permission
        """
        return permission in self.permissions
    
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN
    
    def can_manage_project(self, project: "Project") -> bool:
        """
        Check if user can manage a project.
        
        Args:
            project: The project to check
            
        Returns:
            bool: True if user can manage the project
        """
        return (
            self.is_admin() or
            self.role == UserRole.MANAGER or
            project.owner_id == self.id
        )
