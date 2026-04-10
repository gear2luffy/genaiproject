"""
Task service for task management operations.

Demonstrates:
- Complex business logic
- Multiple relationship handling
- Filtering and sorting
- Bulk operations
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task, TaskStatus, TaskPriority
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilter
from app.services.base import BaseRepository
from app.core.exceptions import NotFoundError, AuthorizationError, ValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class TaskRepository(BaseRepository[Task]):
    """Repository for Task model with specialized queries."""
    
    def __init__(self, db: AsyncSession) -> None:
        """Initialize with Task model."""
        super().__init__(Task, db)
    
    async def get_with_relationships(self, task_id: int) -> Optional[Task]:
        """Get task with all relationships loaded."""
        query = (
            select(Task)
            .where(Task.id == task_id)
            .where(Task.is_deleted == False)  # noqa: E712
            .options(
                selectinload(Task.project),
                selectinload(Task.assignee),
                selectinload(Task.creator)
            )
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_project_tasks(
        self,
        project_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get all tasks for a project."""
        query = (
            select(Task)
            .where(Task.project_id == project_id)
            .where(Task.is_deleted == False)  # noqa: E712
            .options(
                selectinload(Task.assignee),
                selectinload(Task.creator)
            )
            .offset(skip)
            .limit(limit)
            .order_by(Task.created_at.desc())
        )
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def get_user_tasks(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get all tasks assigned to a user."""
        query = (
            select(Task)
            .where(Task.assignee_id == user_id)
            .where(Task.is_deleted == False)  # noqa: E712
            .options(
                selectinload(Task.project),
                selectinload(Task.creator)
            )
            .offset(skip)
            .limit(limit)
            .order_by(Task.due_date.asc().nullslast())
        )
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def search_tasks(
        self,
        filters: TaskFilter,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Task], int]:
        """
        Search and filter tasks.
        
        Args:
            filters: Task filter parameters
            skip: Pagination offset
            limit: Maximum results
            sort_by: Field to sort by
            sort_order: Sort direction
            
        Returns:
            Tuple of tasks list and total count
        """
        conditions = [Task.is_deleted == False]  # noqa: E712
        
        if filters.project_id:
            conditions.append(Task.project_id == filters.project_id)
        
        if filters.status:
            conditions.append(Task.status == filters.status)
        
        if filters.priority:
            conditions.append(Task.priority == filters.priority)
        
        if filters.assignee_id:
            conditions.append(Task.assignee_id == filters.assignee_id)
        
        if filters.created_by:
            conditions.append(Task.created_by == filters.created_by)
        
        if filters.search:
            search_pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern)
                )
            )
        
        if filters.due_before:
            conditions.append(Task.due_date <= filters.due_before)
        
        if filters.due_after:
            conditions.append(Task.due_date >= filters.due_after)
        
        if filters.is_overdue:
            conditions.append(
                and_(
                    Task.due_date < datetime.utcnow(),
                    Task.status != TaskStatus.COMPLETED
                )
            )
        
        base_query = select(Task).where(*conditions)
        
        # Count query
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self._db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Build sort column
        sort_column = getattr(Task, sort_by, Task.created_at)
        if sort_order == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()
        
        # Data query with pagination and relationships
        data_query = (
            base_query
            .options(
                selectinload(Task.project),
                selectinload(Task.assignee),
                selectinload(Task.creator)
            )
            .offset(skip)
            .limit(limit)
            .order_by(sort_column)
        )
        data_result = await self._db.execute(data_query)
        tasks = list(data_result.scalars().all())
        
        return tasks, total
    
    async def count_by_status(
        self,
        project_id: Optional[int] = None
    ) -> dict[str, int]:
        """Get task counts grouped by status."""
        conditions = [Task.is_deleted == False]  # noqa: E712
        if project_id:
            conditions.append(Task.project_id == project_id)
        
        query = (
            select(Task.status, func.count(Task.id))
            .where(*conditions)
            .group_by(Task.status)
        )
        result = await self._db.execute(query)
        return {str(row[0].value): row[1] for row in result.all()}


class TaskService:
    """
    Service class for task management.
    
    Demonstrates:
    - Complex business logic
    - Status transitions
    - Notification triggers
    - Bulk operations
    """
    
    def __init__(self, db: AsyncSession) -> None:
        """Initialize task service."""
        self._db = db
        self._repository = TaskRepository(db)
    
    async def create_task(
        self,
        task_data: TaskCreate,
        created_by: int
    ) -> Task:
        """
        Create a new task.
        
        Args:
            task_data: Task creation schema
            created_by: ID of the creating user
            
        Returns:
            Task: The created task
        """
        # Verify project exists
        from app.services.project_service import ProjectService
        project_service = ProjectService(self._db)
        await project_service.get_project(task_data.project_id)
        
        # Create task
        task_dict = task_data.model_dump()
        task_dict["created_by"] = created_by
        
        task = await self._repository.create(task_dict)
        
        # Reload with relationships
        task = await self._repository.get_with_relationships(task.id)
        
        logger.info(
            "Task created",
            task_id=task.id,
            title=task.title,
            project_id=task.project_id
        )
        
        return task
    
    async def get_task(self, task_id: int) -> Task:
        """
        Get task by ID.
        
        Args:
            task_id: The task ID
            
        Returns:
            Task: The task
            
        Raises:
            NotFoundError: If task not found
        """
        task = await self._repository.get_with_relationships(task_id)
        if not task:
            raise NotFoundError("Task", task_id)
        return task
    
    async def get_tasks(
        self,
        filters: Optional[TaskFilter] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Task], int]:
        """
        Get tasks with filtering and sorting.
        
        Args:
            filters: Optional filter parameters
            skip: Pagination offset
            limit: Maximum results
            sort_by: Field to sort by
            sort_order: Sort direction
            
        Returns:
            Tuple of tasks list and total count
        """
        if filters is None:
            filters = TaskFilter()
        
        return await self._repository.search_tasks(
            filters=filters,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
    
    async def get_project_tasks(
        self,
        project_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get all tasks for a project."""
        return await self._repository.get_project_tasks(
            project_id, skip, limit
        )
    
    async def get_user_tasks(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get all tasks assigned to a user."""
        return await self._repository.get_user_tasks(user_id, skip, limit)
    
    async def update_task(
        self,
        task_id: int,
        task_data: TaskUpdate,
        current_user: User
    ) -> Task:
        """
        Update task details.
        
        Args:
            task_id: The task ID
            task_data: Update schema
            current_user: The user making the request
            
        Returns:
            Task: The updated task
        """
        task = await self.get_task(task_id)
        
        # Check permission
        self._check_task_permission(task, current_user)
        
        update_dict = task_data.model_dump(exclude_unset=True)
        
        # Handle status change completion timestamp
        if task_data.status == TaskStatus.COMPLETED and task.status != TaskStatus.COMPLETED:
            update_dict["completed_at"] = datetime.utcnow()
        elif task_data.status and task_data.status != TaskStatus.COMPLETED:
            update_dict["completed_at"] = None
        
        if update_dict:
            await self._repository.update(task_id, update_dict)
        
        # Reload with relationships
        task = await self._repository.get_with_relationships(task_id)
        
        logger.info("Task updated", task_id=task_id)
        return task
    
    async def delete_task(
        self,
        task_id: int,
        current_user: User
    ) -> bool:
        """
        Soft delete a task.
        
        Args:
            task_id: The task ID
            current_user: The user making the request
            
        Returns:
            bool: True if deleted
        """
        task = await self.get_task(task_id)
        self._check_task_permission(task, current_user)
        
        task.soft_delete()
        await self._db.flush()
        
        logger.info("Task deleted", task_id=task_id)
        return True
    
    async def assign_task(
        self,
        task_id: int,
        assignee_id: int,
        current_user: User
    ) -> Task:
        """
        Assign a task to a user.
        
        Args:
            task_id: The task ID
            assignee_id: ID of the user to assign
            current_user: The user making the request
            
        Returns:
            Task: The updated task
        """
        task = await self.get_task(task_id)
        self._check_task_permission(task, current_user)
        
        task.assign_to(assignee_id)
        await self._db.flush()
        
        logger.info(
            "Task assigned",
            task_id=task_id,
            assignee_id=assignee_id
        )
        
        return await self._repository.get_with_relationships(task_id)
    
    async def unassign_task(
        self,
        task_id: int,
        current_user: User
    ) -> Task:
        """Remove task assignment."""
        task = await self.get_task(task_id)
        self._check_task_permission(task, current_user)
        
        task.unassign()
        await self._db.flush()
        
        return await self._repository.get_with_relationships(task_id)
    
    async def change_task_status(
        self,
        task_id: int,
        new_status: TaskStatus,
        current_user: User
    ) -> Task:
        """
        Change task status.
        
        Args:
            task_id: The task ID
            new_status: The new status
            current_user: The user making the request
            
        Returns:
            Task: The updated task
        """
        task = await self.get_task(task_id)
        self._check_task_permission(task, current_user)
        
        # Validate status transition
        self._validate_status_transition(task.status, new_status)
        
        # Update status
        update_data = {"status": new_status}
        if new_status == TaskStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
        elif task.status == TaskStatus.COMPLETED:
            update_data["completed_at"] = None
        
        await self._repository.update(task_id, update_data)
        
        logger.info(
            "Task status changed",
            task_id=task_id,
            old_status=task.status.value,
            new_status=new_status.value
        )
        
        return await self._repository.get_with_relationships(task_id)
    
    async def bulk_update_status(
        self,
        task_ids: List[int],
        new_status: TaskStatus,
        current_user: User
    ) -> int:
        """
        Bulk update task statuses.
        
        Args:
            task_ids: List of task IDs
            new_status: The new status
            current_user: The user making the request
            
        Returns:
            int: Number of tasks updated
        """
        updated_count = 0
        
        for task_id in task_ids:
            try:
                await self.change_task_status(task_id, new_status, current_user)
                updated_count += 1
            except (NotFoundError, AuthorizationError):
                continue
        
        logger.info(
            "Bulk status update completed",
            total=len(task_ids),
            updated=updated_count,
            status=new_status.value
        )
        
        return updated_count
    
    async def get_task_statistics(
        self,
        project_id: Optional[int] = None
    ) -> dict:
        """
        Get task statistics.
        
        Args:
            project_id: Optional project to filter by
            
        Returns:
            dict: Task statistics
        """
        status_counts = await self._repository.count_by_status(project_id)
        
        total = sum(status_counts.values())
        completed = status_counts.get("completed", 0)
        
        return {
            "total": total,
            "by_status": status_counts,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        }
    
    def _check_task_permission(self, task: Task, user: User) -> None:
        """
        Check if user can modify a task.
        
        Args:
            task: The task to check
            user: The user to verify
            
        Raises:
            AuthorizationError: If user cannot modify task
        """
        # Admins and managers can modify any task
        if user.is_admin() or user.role.value == "manager":
            return
        
        # Task creator can modify
        if task.created_by == user.id:
            return
        
        # Task assignee can modify
        if task.assignee_id == user.id:
            return
        
        # Project owner can modify
        if task.project.owner_id == user.id:
            return
        
        raise AuthorizationError(
            message="You don't have permission to modify this task"
        )
    
    def _validate_status_transition(
        self,
        current: TaskStatus,
        new: TaskStatus
    ) -> None:
        """
        Validate status transition is allowed.
        
        Args:
            current: Current task status
            new: New task status
            
        Raises:
            ValidationError: If transition is not allowed
        """
        # Define allowed transitions
        allowed_transitions = {
            TaskStatus.TODO: [
                TaskStatus.IN_PROGRESS,
                TaskStatus.BLOCKED,
                TaskStatus.CANCELLED
            ],
            TaskStatus.IN_PROGRESS: [
                TaskStatus.TODO,
                TaskStatus.IN_REVIEW,
                TaskStatus.BLOCKED,
                TaskStatus.COMPLETED,
                TaskStatus.CANCELLED
            ],
            TaskStatus.IN_REVIEW: [
                TaskStatus.IN_PROGRESS,
                TaskStatus.COMPLETED,
                TaskStatus.CANCELLED
            ],
            TaskStatus.BLOCKED: [
                TaskStatus.TODO,
                TaskStatus.IN_PROGRESS,
                TaskStatus.CANCELLED
            ],
            TaskStatus.COMPLETED: [
                TaskStatus.IN_PROGRESS,
                TaskStatus.TODO
            ],
            TaskStatus.CANCELLED: [
                TaskStatus.TODO
            ]
        }
        
        if new not in allowed_transitions.get(current, []):
            raise ValidationError(
                message=f"Cannot transition from {current.value} to {new.value}",
                details={
                    "current_status": current.value,
                    "requested_status": new.value,
                    "allowed_transitions": [s.value for s in allowed_transitions.get(current, [])]
                }
            )
