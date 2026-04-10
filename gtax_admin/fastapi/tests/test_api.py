"""
Integration tests for Project and Task API endpoints.

Demonstrates:
- CRUD operation testing
- Authorization testing
- Relationship testing
"""

import pytest
from httpx import AsyncClient

from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.task import Task, TaskStatus, TaskPriority


@pytest.fixture
async def test_project(test_db, test_user) -> Project:
    """Create a test project."""
    project = Project(
        name="Test Project",
        description="A test project",
        slug="test-project",
        status=ProjectStatus.ACTIVE,
        owner_id=test_user.id
    )
    test_db.add(project)
    await test_db.commit()
    await test_db.refresh(project)
    return project


@pytest.fixture
async def test_task(test_db, test_project, test_user) -> Task:
    """Create a test task."""
    task = Task(
        title="Test Task",
        description="A test task",
        project_id=test_project.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        created_by=test_user.id
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)
    return task


class TestProjectEndpoints:
    """Integration tests for /api/v1/projects endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_project(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test project creation."""
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "New Project",
                "description": "A brand new project"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Project"
        assert data["slug"] == "new-project"
        assert data["status"] == "planning"
    
    @pytest.mark.asyncio
    async def test_create_project_unauthorized(self, client: AsyncClient):
        """Test project creation without authentication."""
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Unauthorized Project"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_list_projects(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project
    ):
        """Test listing projects."""
        response = await client.get(
            "/api/v1/projects",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_project(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project
    ):
        """Test getting a single project."""
        response = await client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_project.id
        assert data["name"] == test_project.name
    
    @pytest.mark.asyncio
    async def test_get_project_by_slug(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project
    ):
        """Test getting project by slug."""
        response = await client.get(
            f"/api/v1/projects/slug/{test_project.slug}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == test_project.id
    
    @pytest.mark.asyncio
    async def test_update_project(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project
    ):
        """Test updating a project."""
        response = await client.put(
            f"/api/v1/projects/{test_project.id}",
            json={"name": "Updated Project Name"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Project Name"
    
    @pytest.mark.asyncio
    async def test_delete_project(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project
    ):
        """Test deleting a project."""
        response = await client.delete(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify project is deleted
        get_response = await client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


class TestTaskEndpoints:
    """Integration tests for /api/v1/tasks endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_task(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project
    ):
        """Test task creation."""
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "New Task",
                "description": "A new task",
                "project_id": test_project.id,
                "priority": "high"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["status"] == "todo"
        assert data["priority"] == "high"
        assert data["project_id"] == test_project.id
    
    @pytest.mark.asyncio
    async def test_list_tasks(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_task: Task
    ):
        """Test listing tasks."""
        response = await client.get(
            "/api/v1/tasks",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_list_tasks_with_filters(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_task: Task,
        test_project: Project
    ):
        """Test listing tasks with filters."""
        response = await client.get(
            "/api/v1/tasks",
            params={
                "project_id": test_project.id,
                "status": "todo"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        for task in data["items"]:
            assert task["project_id"] == test_project.id
            assert task["status"] == "todo"
    
    @pytest.mark.asyncio
    async def test_get_task(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_task: Task
    ):
        """Test getting a single task."""
        response = await client.get(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == test_task.title
    
    @pytest.mark.asyncio
    async def test_update_task(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_task: Task
    ):
        """Test updating a task."""
        response = await client.put(
            f"/api/v1/tasks/{test_task.id}",
            json={
                "title": "Updated Task",
                "priority": "critical"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["priority"] == "critical"
    
    @pytest.mark.asyncio
    async def test_change_task_status(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_task: Task
    ):
        """Test changing task status."""
        response = await client.patch(
            f"/api/v1/tasks/{test_task.id}/status",
            json={"status": "in_progress"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"
    
    @pytest.mark.asyncio
    async def test_assign_task(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_task: Task,
        test_user: User
    ):
        """Test assigning task to user."""
        response = await client.patch(
            f"/api/v1/tasks/{test_task.id}/assign",
            json={"assignee_id": test_user.id},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["assignee_id"] == test_user.id
    
    @pytest.mark.asyncio
    async def test_delete_task(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_task: Task
    ):
        """Test deleting a task."""
        response = await client.delete(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify task is deleted
        get_response = await client.get(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_project_tasks(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_task: Task,
        test_project: Project
    ):
        """Test getting all tasks for a project."""
        response = await client.get(
            f"/api/v1/tasks/project/{test_project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(t["project_id"] == test_project.id for t in data)


class TestHealthEndpoints:
    """Integration tests for health check endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "services" in data
    
    @pytest.mark.asyncio
    async def test_liveness_check(self, client: AsyncClient):
        """Test liveness check endpoint."""
        response = await client.get("/api/v1/health/live")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_readiness_check(self, client: AsyncClient):
        """Test readiness check endpoint."""
        response = await client.get("/api/v1/health/ready")
        
        assert response.status_code == 200
