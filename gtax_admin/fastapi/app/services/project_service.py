"""
Project service for project management operations.

Demonstrates:
- Complex queries with relationships
- Business logic validation
- Authorization checks
"""

import re
from typing import List, Optional, Tuple

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectStatus
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.base import BaseRepository
from app.core.exceptions import ConflictError, NotFoundError, AuthorizationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project model with specialized queries."""
    
    def __init__(self, db: AsyncSession) -> None:
        """Initialize with Project model."""
        super().__init__(Project, db)
    
    async def get_by_slug(self, slug: str) -> Optional[Project]:
        """Get project by URL slug."""
        query = (
            select(Project)
            .where(Project.slug == slug)
            .where(Project.is_deleted == False)  # noqa: E712
            .options(selectinload(Project.owner))
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_with_relationships(self, project_id: int) -> Optional[Project]:
        """Get project with owner and tasks loaded."""
        query = (
            select(Project)
            .where(Project.id == project_id)
            .where(Project.is_deleted == False)  # noqa: E712
            .options(
                selectinload(Project.owner),
                selectinload(Project.tasks)
            )
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_projects(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """Get all projects owned by a user."""
        query = (
            select(Project)
            .where(Project.owner_id == user_id)
            .where(Project.is_deleted == False)  # noqa: E712
            .options(selectinload(Project.owner))
            .offset(skip)
            .limit(limit)
        )
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def search_projects(
        self,
        search_term: Optional[str] = None,
        status: Optional[ProjectStatus] = None,
        owner_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Project], int]:
        """
        Search and filter projects.
        
        Args:
            search_term: Search in name and description
            status: Filter by status
            owner_id: Filter by owner
            skip: Pagination offset
            limit: Maximum results
            
        Returns:
            Tuple of projects list and total count
        """
        # Build base query
        conditions = [Project.is_deleted == False]  # noqa: E712
        
        if search_term:
            search_pattern = f"%{search_term}%"
            conditions.append(
                or_(
                    Project.name.ilike(search_pattern),
                    Project.description.ilike(search_pattern)
                )
            )
        
        if status:
            conditions.append(Project.status == status)
        
        if owner_id:
            conditions.append(Project.owner_id == owner_id)
        
        base_query = select(Project).where(*conditions)
        
        # Count query
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self._db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Data query with pagination and relationships
        data_query = (
            base_query
            .options(selectinload(Project.owner))
            .offset(skip)
            .limit(limit)
            .order_by(Project.created_at.desc())
        )
        data_result = await self._db.execute(data_query)
        projects = list(data_result.scalars().all())
        
        return projects, total


class ProjectService:
    """
    Service class for project management.
    
    Demonstrates:
    - Business logic for project operations
    - Slug generation and validation
    - Authorization checks
    """
    
    def __init__(self, db: AsyncSession) -> None:
        """Initialize project service."""
        self._db = db
        self._repository = ProjectRepository(db)
    
    def _generate_slug(self, name: str) -> str:
        """
        Generate URL-friendly slug from project name.
        
        Args:
            name: Project name
            
        Returns:
            str: URL-friendly slug
        """
        slug = name.lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")
    
    async def _ensure_unique_slug(self, slug: str, exclude_id: Optional[int] = None) -> str:
        """
        Ensure slug is unique, adding suffix if needed.
        
        Args:
            slug: Base slug
            exclude_id: Project ID to exclude from check
            
        Returns:
            str: Unique slug
        """
        original_slug = slug
        counter = 1
        
        while True:
            existing = await self._repository.get_by_slug(slug)
            if not existing or (exclude_id and existing.id == exclude_id):
                return slug
            
            slug = f"{original_slug}-{counter}"
            counter += 1
    
    async def create_project(
        self,
        project_data: ProjectCreate,
        owner_id: int
    ) -> Project:
        """
        Create a new project.
        
        Args:
            project_data: Project creation schema
            owner_id: ID of the project owner
            
        Returns:
            Project: The created project
        """
        # Generate and ensure unique slug
        if project_data.slug:
            slug = project_data.slug
        else:
            slug = self._generate_slug(project_data.name)
        
        slug = await self._ensure_unique_slug(slug)
        
        # Create project
        project_dict = project_data.model_dump(exclude={"slug"})
        project_dict["slug"] = slug
        project_dict["owner_id"] = owner_id
        
        project = await self._repository.create(project_dict)
        logger.info(
            "Project created",
            project_id=project.id,
            name=project.name,
            owner_id=owner_id
        )
        
        return project
    
    async def get_project(self, project_id: int) -> Project:
        """
        Get project by ID.
        
        Args:
            project_id: The project ID
            
        Returns:
            Project: The project
            
        Raises:
            NotFoundError: If project not found
        """
        project = await self._repository.get_with_relationships(project_id)
        if not project:
            raise NotFoundError("Project", project_id)
        return project
    
    async def get_project_by_slug(self, slug: str) -> Project:
        """
        Get project by URL slug.
        
        Args:
            slug: The project slug
            
        Returns:
            Project: The project
            
        Raises:
            NotFoundError: If project not found
        """
        project = await self._repository.get_by_slug(slug)
        if not project:
            raise NotFoundError("Project", slug)
        return project
    
    async def get_projects(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[ProjectStatus] = None,
        owner_id: Optional[int] = None
    ) -> Tuple[List[Project], int]:
        """
        Get projects with filtering.
        
        Args:
            skip: Pagination offset
            limit: Maximum results
            search: Search term
            status: Status filter
            owner_id: Owner filter
            
        Returns:
            Tuple of projects list and total count
        """
        return await self._repository.search_projects(
            search_term=search,
            status=status,
            owner_id=owner_id,
            skip=skip,
            limit=limit
        )
    
    async def update_project(
        self,
        project_id: int,
        project_data: ProjectUpdate,
        current_user: User
    ) -> Project:
        """
        Update project details.
        
        Args:
            project_id: The project ID
            project_data: Update schema
            current_user: The user making the request
            
        Returns:
            Project: The updated project
            
        Raises:
            NotFoundError: If project not found
            AuthorizationError: If user cannot modify project
        """
        project = await self.get_project(project_id)
        
        # Check authorization
        if not current_user.can_manage_project(project):
            raise AuthorizationError(
                message="You don't have permission to modify this project"
            )
        
        update_dict = project_data.model_dump(exclude_unset=True)
        
        if update_dict:
            updated_project = await self._repository.update(project_id, update_dict)
            logger.info("Project updated", project_id=project_id)
            return updated_project
        
        return project
    
    async def delete_project(
        self,
        project_id: int,
        current_user: User
    ) -> bool:
        """
        Soft delete a project.
        
        Args:
            project_id: The project ID
            current_user: The user making the request
            
        Returns:
            bool: True if deleted
            
        Raises:
            NotFoundError: If project not found
            AuthorizationError: If user cannot delete project
        """
        project = await self.get_project(project_id)
        
        # Check authorization
        if not current_user.can_manage_project(project):
            raise AuthorizationError(
                message="You don't have permission to delete this project"
            )
        
        project.soft_delete()
        await self._db.flush()
        
        logger.info("Project deleted", project_id=project_id)
        return True
    
    async def change_project_status(
        self,
        project_id: int,
        new_status: ProjectStatus,
        current_user: User
    ) -> Project:
        """
        Change project status.
        
        Args:
            project_id: The project ID
            new_status: The new status
            current_user: The user making the request
            
        Returns:
            Project: The updated project
        """
        project = await self.get_project(project_id)
        
        if not current_user.can_manage_project(project):
            raise AuthorizationError(
                message="You don't have permission to change project status"
            )
        
        project.status = new_status
        await self._db.flush()
        
        logger.info(
            "Project status changed",
            project_id=project_id,
            new_status=new_status.value
        )
        
        return project
