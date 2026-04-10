# FastAPI Task Management API
## Complete Technical Documentation & Interview Preparation Guide

---

# Table of Contents

1. [Executive Summary](#executive-summary)
2. [Project Overview](#project-overview)
3. [Architecture & Design Patterns](#architecture--design-patterns)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Core Modules Deep Dive](#core-modules-deep-dive)
7. [API Endpoints Reference](#api-endpoints-reference)
8. [Database Design](#database-design)
9. [Authentication & Security](#authentication--security)
10. [Testing Strategy](#testing-strategy)
11. [DevOps & Deployment](#devops--deployment)
12. [Python Concepts Demonstrated](#python-concepts-demonstrated)
13. [FastAPI Concepts Demonstrated](#fastapi-concepts-demonstrated)
14. [Interview Questions & Answers](#interview-questions--answers)

---

# Executive Summary

This document provides comprehensive documentation for a **production-ready Task Management API** built with FastAPI. The project demonstrates industry best practices in Python web development, including clean architecture, comprehensive testing, security implementation, and DevOps practices.

**Key Highlights:**
- Full-featured REST API with JWT authentication
- Async/await patterns throughout the codebase
- Repository pattern for data access
- Role-based access control (RBAC)
- Real-time WebSocket support
- Docker containerization
- Comprehensive test coverage

---

# Project Overview

## Purpose
A Task Management API that allows organizations to:
- Manage users with different roles (Admin, Manager, User)
- Create and organize projects
- Create, assign, and track tasks
- Receive real-time notifications via WebSocket

## Business Requirements
1. User registration and authentication
2. Project creation and management
3. Task creation with priorities and due dates
4. Task assignment to users
5. Task status tracking (Todo → In Progress → Done)
6. File attachments for tasks
7. Real-time updates for task changes

---

# Architecture & Design Patterns

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│              (API Routes, Request/Response)                  │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
│              (Services, Business Logic)                      │
├─────────────────────────────────────────────────────────────┤
│                    Domain Layer                              │
│              (Models, Schemas, Validations)                  │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                      │
│              (Database, External Services)                   │
└─────────────────────────────────────────────────────────────┘
```

## Design Patterns Used

### 1. Repository Pattern
Separates data access logic from business logic.

```python
class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get(self, id: int) -> Optional[ModelType]:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
```

### 2. Dependency Injection
FastAPI's DI system for loose coupling.

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    # Validate token and return user
```

### 3. Factory Pattern
Service factory for creating service instances.

```python
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)
```

### 4. Strategy Pattern
Different authentication strategies (JWT, API Key).

### 5. Decorator Pattern
Cross-cutting concerns like logging and timing.

```python
def log_execution(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"Executing {func.__name__}")
        result = await func(*args, **kwargs)
        logger.info(f"Completed {func.__name__}")
        return result
    return wrapper
```

---

# Technology Stack

## Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | FastAPI | 0.109+ | Web framework with async support |
| **Language** | Python | 3.11+ | Core programming language |
| **Database** | PostgreSQL | 15+ | Primary production database |
| **ORM** | SQLAlchemy | 2.0+ | Async database operations |
| **Migrations** | Alembic | 1.13+ | Database schema management |
| **Validation** | Pydantic | 2.x | Data validation and settings |
| **Auth** | python-jose | 3.3+ | JWT token handling |
| **Password** | passlib | 1.7+ | Password hashing (bcrypt) |
| **Testing** | pytest | 8.0+ | Test framework |
| **Server** | Uvicorn | 0.27+ | ASGI server |
| **Logging** | structlog | 24.1+ | Structured logging |

## Development Tools

| Tool | Purpose |
|------|---------|
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |
| Pre-commit | Git hooks for code quality |
| Black | Code formatting |
| Ruff | Linting and import sorting |
| mypy | Static type checking |

---

# Project Structure

```
fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py        # Authentication endpoints
│   │           ├── users.py       # User management
│   │           ├── projects.py    # Project CRUD
│   │           ├── tasks.py       # Task management
│   │           ├── files.py       # File upload/download
│   │           ├── websocket.py   # Real-time updates
│   │           └── health.py      # Health checks
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Pydantic Settings
│   │   ├── security.py            # JWT, password hashing
│   │   ├── logging.py             # Structlog configuration
│   │   └── exceptions.py          # Custom exceptions
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # Base model, mixins
│   │   ├── user.py                # User model
│   │   ├── project.py             # Project model
│   │   └── task.py                # Task model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py              # Shared schemas
│   │   ├── user.py                # User schemas
│   │   ├── project.py             # Project schemas
│   │   └── task.py                # Task schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base.py                # Base repository
│   │   ├── user_service.py        # User business logic
│   │   ├── project_service.py     # Project business logic
│   │   ├── task_service.py        # Task business logic
│   │   └── auth_service.py        # Authentication logic
│   │
│   ├── dependencies/
│   │   ├── __init__.py
│   │   ├── auth.py                # Auth dependencies
│   │   ├── pagination.py          # Pagination helpers
│   │   └── services.py            # Service factories
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py            # Database configuration
│   │
│   └── utils/
│       ├── __init__.py
│       ├── middleware.py          # Custom middleware
│       ├── helpers.py             # Utility functions
│       └── decorators.py          # Custom decorators
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Test fixtures
│   ├── test_auth_api.py           # Auth tests
│   ├── test_api.py                # Integration tests
│   └── test_user_service.py       # Unit tests
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── scripts/
│   └── init-db.sql
│
├── uploads/                       # File uploads directory
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .pre-commit-config.yaml
├── pyproject.toml
├── pytest.ini
├── alembic.ini
└── README.md
```

---

# Core Modules Deep Dive

## 1. Configuration Management (core/config.py)

Uses Pydantic Settings for type-safe configuration with environment variable support.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    APP_NAME: str = "Task Management API"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./task_management.db"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
```

**Key Features:**
- Type validation on startup
- Automatic environment variable loading
- Default values with override capability
- Computed properties for derived values

## 2. Security Module (core/security.py)

Handles JWT token management and password hashing.

```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityManager:
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.settings.SECRET_KEY, algorithm="HS256")
```

**Security Features:**
- Bcrypt password hashing with automatic salt
- JWT with expiration and token type
- Refresh token support for seamless re-authentication
- Token blacklisting capability

## 3. Database Setup (db/database.py)

Async SQLAlchemy configuration with connection pooling.

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
```

**Connection Pool Settings:**
- `pool_size=5`: Maintain 5 persistent connections
- `max_overflow=10`: Allow 10 additional connections under load
- `pool_pre_ping=True`: Verify connection health before use

## 4. Custom Exceptions (core/exceptions.py)

Hierarchical exception system for clean error handling.

```python
class AppException(Exception):
    """Base exception for application errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(AppException):
    def __init__(self, resource: str, id: Any):
        super().__init__(f"{resource} with id {id} not found", 404)

class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)

class AuthorizationError(AppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, 403)

class ValidationError(AppException):
    def __init__(self, message: str):
        super().__init__(message, 422)
```

---

# API Endpoints Reference

## Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login and get tokens | No |
| POST | `/api/v1/auth/refresh` | Refresh access token | Yes (Refresh) |
| POST | `/api/v1/auth/logout` | Invalidate tokens | Yes |
| GET | `/api/v1/auth/me` | Get current user | Yes |

## User Endpoints

| Method | Endpoint | Description | Auth Required | Roles |
|--------|----------|-------------|---------------|-------|
| GET | `/api/v1/users` | List all users | Yes | Admin |
| GET | `/api/v1/users/{id}` | Get user by ID | Yes | Admin, Self |
| PUT | `/api/v1/users/{id}` | Update user | Yes | Admin, Self |
| DELETE | `/api/v1/users/{id}` | Delete user | Yes | Admin |
| PATCH | `/api/v1/users/{id}/role` | Change user role | Yes | Admin |

## Project Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/projects` | Create project | Yes |
| GET | `/api/v1/projects` | List projects | Yes |
| GET | `/api/v1/projects/{id}` | Get project details | Yes |
| PUT | `/api/v1/projects/{id}` | Update project | Yes (Owner/Admin) |
| DELETE | `/api/v1/projects/{id}` | Delete project | Yes (Owner/Admin) |
| GET | `/api/v1/projects/{id}/tasks` | List project tasks | Yes |
| POST | `/api/v1/projects/{id}/members` | Add project member | Yes (Owner/Admin) |

## Task Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/tasks` | Create task | Yes |
| GET | `/api/v1/tasks` | List tasks (with filters) | Yes |
| GET | `/api/v1/tasks/{id}` | Get task details | Yes |
| PUT | `/api/v1/tasks/{id}` | Update task | Yes |
| DELETE | `/api/v1/tasks/{id}` | Delete task | Yes |
| PATCH | `/api/v1/tasks/{id}/status` | Update task status | Yes |
| PATCH | `/api/v1/tasks/{id}/assign` | Assign task to user | Yes |

## File Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/files/upload` | Upload file | Yes |
| GET | `/api/v1/files/{filename}` | Download file | Yes |
| DELETE | `/api/v1/files/{filename}` | Delete file | Yes |

## WebSocket Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/v1/ws/connect` | WebSocket connection for real-time updates |

## Health Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Basic health check | No |
| GET | `/health/ready` | Readiness check (DB) | No |
| GET | `/health/live` | Liveness check | No |

---

# Database Design

## Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│    users     │       │   projects   │       │    tasks     │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │       │ id (PK)      │
│ email        │◄──────│ owner_id(FK) │       │ project_id(FK)│───►│
│ username     │       │ name         │◄──────│ assignee_id  │───►│
│ hashed_pass  │       │ description  │       │ creator_id   │───►│
│ full_name    │       │ status       │       │ title        │
│ role         │       │ created_at   │       │ description  │
│ is_active    │       │ updated_at   │       │ status       │
│ is_verified  │       │ deleted_at   │       │ priority     │
│ created_at   │       └──────────────┘       │ due_date     │
│ updated_at   │                              │ created_at   │
│ deleted_at   │                              │ updated_at   │
└──────────────┘                              │ deleted_at   │
                                              └──────────────┘
```

## Model Definitions

### User Model
```python
class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    
    # Relationships
    owned_projects: Mapped[list["Project"]] = relationship(back_populates="owner")
    assigned_tasks: Mapped[list["Task"]] = relationship(back_populates="assignee")
```

### Project Model
```python
class Project(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(default=ProjectStatus.ACTIVE)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Relationships
    owner: Mapped["User"] = relationship(back_populates="owned_projects")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project")
```

### Task Model
```python
class Task(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.TODO)
    priority: Mapped[TaskPriority] = mapped_column(default=TaskPriority.MEDIUM)
    due_date: Mapped[Optional[datetime]] = mapped_column()
    
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="tasks")
    creator: Mapped["User"] = relationship(foreign_keys=[creator_id])
    assignee: Mapped[Optional["User"]] = relationship(back_populates="assigned_tasks")
```

## Mixins

### TimestampMixin
Automatically tracks creation and modification times.

```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now()
    )
```

### SoftDeleteMixin
Implements soft delete pattern.

```python
class SoftDeleteMixin:
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    @hybrid_property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
```

---

# Authentication & Security

## JWT Token Flow

```
┌─────────┐                    ┌─────────┐                    ┌──────────┐
│ Client  │                    │   API   │                    │ Database │
└────┬────┘                    └────┬────┘                    └────┬─────┘
     │                              │                              │
     │ POST /auth/login             │                              │
     │ {email, password}            │                              │
     │─────────────────────────────►│                              │
     │                              │ SELECT user WHERE email=...  │
     │                              │─────────────────────────────►│
     │                              │                              │
     │                              │◄─────────────────────────────│
     │                              │    User record               │
     │                              │                              │
     │                              │ verify_password()            │
     │                              │ create_tokens()              │
     │                              │                              │
     │◄─────────────────────────────│                              │
     │ {access_token, refresh_token}│                              │
     │                              │                              │
     │ GET /projects                │                              │
     │ Authorization: Bearer token  │                              │
     │─────────────────────────────►│                              │
     │                              │ decode_jwt()                 │
     │                              │ get_user()                   │
     │                              │─────────────────────────────►│
     │                              │◄─────────────────────────────│
     │                              │                              │
     │◄─────────────────────────────│                              │
     │     Projects response        │                              │
```

## Password Hashing

Using bcrypt with automatic salt:

```python
# Hashing
hashed = pwd_context.hash("plaintext_password")
# Result: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTt

# Verification
is_valid = pwd_context.verify("plaintext_password", hashed)
```

## Role-Based Access Control (RBAC)

### Role Hierarchy
```
Admin
  └── Can manage all users, projects, tasks
  └── Can change user roles
  └── Full system access

Manager
  └── Can manage projects they own
  └── Can assign tasks
  └── Cannot manage users

User
  └── Can create/manage own tasks
  └── Can view assigned projects
  └── Basic access
```

### Permission Checking
```python
class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise AuthorizationError("Insufficient permissions")
        return user

# Usage
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(RoleChecker([UserRole.ADMIN]))
):
    ...
```

## Security Headers

Applied via middleware:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`

---

# Testing Strategy

## Test Types

### 1. Unit Tests
Test individual functions/methods in isolation.

```python
# test_user_service.py
@pytest.mark.asyncio
async def test_create_user(user_service, sample_user_data):
    user = await user_service.create_user(sample_user_data)
    
    assert user.email == sample_user_data.email
    assert user.username == sample_user_data.username
    assert user.hashed_password != sample_user_data.password

@pytest.mark.asyncio
async def test_create_user_duplicate_email(user_service, existing_user):
    with pytest.raises(ValidationError) as exc_info:
        await user_service.create_user(UserCreate(
            email=existing_user.email,
            username="different",
            password="Password123"
        ))
    
    assert "already exists" in str(exc_info.value)
```

### 2. Integration Tests
Test API endpoints with database.

```python
# test_api.py
@pytest.mark.asyncio
async def test_create_project(client, auth_headers):
    response = await client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "description": "Description"},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_project_unauthorized(client):
    response = await client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    )
    
    assert response.status_code == 401
```

### 3. Authentication Tests
Test auth flows comprehensively.

```python
# test_auth_api.py
@pytest.mark.asyncio
async def test_login_success(client, registered_user):
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": registered_user.email,
            "password": "testpassword"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_password(client, registered_user):
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": registered_user.email,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
```

## Test Fixtures (conftest.py)

```python
@pytest.fixture
async def db_session():
    """Create test database session"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session

@pytest.fixture
async def client(db_session):
    """Create test client"""
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def auth_headers(client, registered_user):
    """Get authentication headers"""
    response = await client.post("/api/v1/auth/login", data={
        "username": registered_user.email,
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth_api.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_login"

# Run async tests only
pytest -m asyncio
```

---

# DevOps & Deployment

## Docker Configuration

### Dockerfile (Multi-stage Build)

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose (Development)

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/taskdb
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./app:/app/app
    command: uvicorn app.main:app --reload --host 0.0.0.0

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: taskdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Database Migrations

### Initial Migration
```bash
# Generate migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# View migration history
alembic history
```

### Migration Best Practices
1. Always review auto-generated migrations
2. Test migrations on copy of production data
3. Include both upgrade and downgrade paths
4. Use transactions for data migrations

## Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        args: [--line-length=100]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, sqlalchemy]
```

---

# Python Concepts Demonstrated

## 1. Object-Oriented Programming

### Classes and Inheritance
```python
# Base class with generic type
class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

# Derived class
class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
```

### Mixins for Code Reuse
```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())

class SoftDeleteMixin:
    deleted_at: Mapped[Optional[datetime]] = mapped_column(default=None)
    
    def soft_delete(self):
        self.deleted_at = datetime.utcnow()

class User(Base, TimestampMixin, SoftDeleteMixin):
    # Inherits from multiple mixins
    pass
```

### Encapsulation
```python
class UserService:
    def __init__(self, db: AsyncSession):
        self._repository = UserRepository(db)
        self._password_hasher = PasswordHasher()
    
    async def create_user(self, data: UserCreate) -> User:
        # Encapsulate password hashing logic
        hashed_password = self._password_hasher.hash(data.password)
        return await self._repository.create({
            **data.model_dump(exclude={"password"}),
            "hashed_password": hashed_password
        })
```

## 2. Type Hints

### Basic Type Annotations
```python
def calculate_total(items: list[float], tax_rate: float = 0.1) -> float:
    subtotal = sum(items)
    return subtotal * (1 + tax_rate)
```

### Generic Types
```python
from typing import TypeVar, Generic, Optional

T = TypeVar("T")

class Result(Generic[T]):
    def __init__(self, value: Optional[T], error: Optional[str] = None):
        self.value = value
        self.error = error
    
    @property
    def is_success(self) -> bool:
        return self.error is None
```

### Annotated for Metadata
```python
from typing import Annotated
from fastapi import Query

PageSize = Annotated[int, Query(ge=1, le=100, default=20)]

async def list_items(page_size: PageSize):
    ...
```

## 3. Decorators

### Function Decorator
```python
import functools
import time

def log_execution(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"{func.__name__} completed in {elapsed:.3f}s")
        return result
    return wrapper

@log_execution
async def process_data(data: list) -> dict:
    ...
```

### Decorator with Parameters
```python
def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(delay * (attempt + 1))
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
async def fetch_external_api():
    ...
```

### Class Decorator
```python
def singleton(cls):
    instances = {}
    
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class ConfigManager:
    ...
```

## 4. Context Managers

### Async Context Manager
```python
class DatabaseTransaction:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def __aenter__(self):
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()

# Usage
async with DatabaseTransaction(session) as db:
    await db.execute(...)
```

### Using contextlib
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def logging_context(operation: str):
    logger.info(f"Starting: {operation}")
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(f"Completed: {operation} in {elapsed:.3f}s")

# Usage
async with logging_context("user_creation"):
    await user_service.create_user(data)
```

## 5. Async/Await

### Concurrent Operations
```python
import asyncio

async def fetch_user_data(user_id: int) -> dict:
    # Fetch user details, projects, and tasks concurrently
    user, projects, tasks = await asyncio.gather(
        user_service.get_user(user_id),
        project_service.get_user_projects(user_id),
        task_service.get_user_tasks(user_id)
    )
    
    return {
        "user": user,
        "projects": projects,
        "tasks": tasks
    }
```

### Async Generators
```python
async def stream_large_dataset(query: str):
    async with get_db() as session:
        result = await session.stream(text(query))
        async for row in result:
            yield row
```

## 6. Exception Handling

### Custom Exception Hierarchy
```python
class AppException(Exception):
    status_code: int = 500
    message: str = "An error occurred"

class NotFoundError(AppException):
    status_code = 404

class ValidationError(AppException):
    status_code = 422

# Exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
```

---

# FastAPI Concepts Demonstrated

## 1. Dependency Injection

### Simple Dependencies
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    ...
```

### Chained Dependencies
```python
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    payload = decode_token(token)
    return await user_service.get_user(payload["sub"])

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return user
```

### Class Dependencies
```python
class Pagination:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100)
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size

@router.get("/items")
async def list_items(pagination: Pagination = Depends()):
    return await service.list(
        offset=pagination.offset,
        limit=pagination.page_size
    )
```

## 2. Pydantic Models

### Request Validation
```python
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v.lower()
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        return v
```

### Response Models
```python
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str]
    role: UserRole
    created_at: datetime

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    ...
```

### Nested Models
```python
class TaskDetail(BaseModel):
    id: int
    title: str
    status: TaskStatus
    assignee: Optional[UserResponse]
    project: ProjectResponse
    
    model_config = ConfigDict(from_attributes=True)
```

## 3. Path Operations

### Query Parameters
```python
@router.get("/tasks")
async def list_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    project_id: Optional[int] = None,
    search: Optional[str] = Query(None, min_length=1),
    sort_by: str = Query("created_at", regex="^(created_at|due_date|priority)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    ...
```

### Path Parameters
```python
@router.get("/users/{user_id}/tasks/{task_id}")
async def get_user_task(
    user_id: int = Path(..., gt=0),
    task_id: int = Path(..., gt=0)
):
    ...
```

### Request Body
```python
@router.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    created_task = await task_service.create(task, current_user)
    background_tasks.add_task(notify_assignee, created_task)
    return created_task
```

## 4. Middleware

### Custom Middleware
```python
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        return response

app.add_middleware(TimingMiddleware)
```

### CORS Middleware
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 5. Background Tasks

```python
from fastapi import BackgroundTasks

def send_email_notification(email: str, subject: str, body: str):
    # Email sending logic
    ...

@router.post("/tasks")
async def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks
):
    created_task = await task_service.create(task)
    
    # Add background task
    background_tasks.add_task(
        send_email_notification,
        task.assignee_email,
        "New Task Assigned",
        f"You have been assigned: {task.title}"
    )
    
    return created_task
```

## 6. WebSocket

```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)
    
    async def broadcast(self, room: str, message: dict):
        for connection in self.active_connections.get(room, []):
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await manager.connect(websocket, room)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(room, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
```

## 7. File Operations

```python
from fastapi import UploadFile, File
from fastapi.responses import FileResponse

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    file_path = f"uploads/{uuid4()}_{file.filename}"
    
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    return {"filename": file.filename, "path": file_path}

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"uploads/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")
    return FileResponse(file_path)
```

## 8. Application Lifespan

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    await database.connect()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
```

---

# Interview Questions & Answers

## Section 1: Python Fundamentals

### Q1: What is the difference between `==` and `is` in Python?
**Answer:**
- `==` compares **values** (equality)
- `is` compares **identity** (same object in memory)

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)  # True - same values
print(a is b)  # False - different objects
print(a is c)  # True - same object
```

### Q2: Explain Python's GIL (Global Interpreter Lock)
**Answer:**
The GIL is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecode simultaneously.

**Implications:**
- CPU-bound tasks don't benefit from threading
- Use `multiprocessing` for CPU-bound parallel tasks
- Async/await is effective for I/O-bound tasks
- GIL is released during I/O operations

**In this project:** We use async/await for I/O-bound database operations, which works well despite the GIL since the GIL is released during await calls.

### Q3: What are `*args` and `**kwargs`?
**Answer:**
- `*args`: Collects positional arguments into a tuple
- `**kwargs`: Collects keyword arguments into a dictionary

```python
def func(*args, **kwargs):
    print(f"args: {args}")      # (1, 2, 3)
    print(f"kwargs: {kwargs}")  # {'name': 'John'}

func(1, 2, 3, name="John")
```

### Q4: Explain Python decorators and their use cases
**Answer:**
Decorators are functions that modify the behavior of other functions/methods.

**Use cases in this project:**
1. **Logging execution time:**
```python
def log_execution(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"Executing {func.__name__}")
        result = await func(*args, **kwargs)
        logger.info(f"Completed {func.__name__}")
        return result
    return wrapper
```

2. **Retry logic:**
```python
@retry(max_attempts=3)
async def call_external_api():
    ...
```

3. **Route decorators:** `@router.get("/users")`

### Q5: What is the difference between `@staticmethod` and `@classmethod`?
**Answer:**
- `@staticmethod`: No access to class or instance (like a plain function)
- `@classmethod`: Receives class as first argument (`cls`)

```python
class MyClass:
    class_var = "class variable"
    
    @staticmethod
    def static_method():
        # Cannot access cls or self
        return "static"
    
    @classmethod
    def class_method(cls):
        # Can access class variables
        return cls.class_var
```

### Q6: Explain list comprehension vs generator expression
**Answer:**
- **List comprehension**: Creates entire list in memory
- **Generator expression**: Creates items on-demand (lazy evaluation)

```python
# List comprehension - all items in memory
squares_list = [x**2 for x in range(1000000)]  # Uses ~8MB

# Generator expression - items created on-demand
squares_gen = (x**2 for x in range(1000000))  # Uses ~120 bytes
```

**When to use:**
- List: Need to access items multiple times, need length
- Generator: Large datasets, single iteration, memory constraints

### Q7: What is Python's Method Resolution Order (MRO)?
**Answer:**
MRO determines the order in which base classes are searched when looking for a method.

```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

class C(A):
    def method(self):
        return "C"

class D(B, C):
    pass

print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
print(D().method())  # "B"
```

Python uses C3 linearization algorithm.

### Q8: Explain the difference between shallow copy and deep copy
**Answer:**
```python
import copy

original = [[1, 2], [3, 4]]

# Shallow copy - new list, same inner lists
shallow = copy.copy(original)
shallow[0][0] = 999
print(original)  # [[999, 2], [3, 4]] - affected!

# Deep copy - new list, new inner lists
original = [[1, 2], [3, 4]]
deep = copy.deepcopy(original)
deep[0][0] = 999
print(original)  # [[1, 2], [3, 4]] - not affected
```

### Q9: What are context managers and how do they work?
**Answer:**
Context managers handle setup and teardown using `__enter__` and `__exit__` methods.

```python
class DatabaseConnection:
    def __enter__(self):
        self.conn = create_connection()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        return False  # Don't suppress exceptions

# Usage
with DatabaseConnection() as conn:
    conn.execute("SELECT * FROM users")
```

**In this project:** Used for database sessions and logging contexts.

### Q10: Explain async/await in Python
**Answer:**
- `async def`: Defines a coroutine function
- `await`: Pauses coroutine until operation completes
- Event loop manages coroutine execution

```python
import asyncio

async def fetch_data(url: str) -> dict:
    await asyncio.sleep(1)  # Simulates I/O
    return {"data": "result"}

async def main():
    # Sequential (2 seconds)
    result1 = await fetch_data("url1")
    result2 = await fetch_data("url2")
    
    # Concurrent (1 second)
    results = await asyncio.gather(
        fetch_data("url1"),
        fetch_data("url2")
    )
```

**Benefits in this project:**
- Non-blocking database operations
- Handle thousands of concurrent requests
- Efficient resource utilization

---

## Section 2: FastAPI Specific

### Q11: What is FastAPI and why would you choose it over Flask/Django?
**Answer:**
FastAPI is a modern Python web framework with:

**Advantages over Flask:**
- Built-in async support
- Automatic OpenAPI documentation
- Type validation with Pydantic
- Dependency injection system
- Higher performance (Starlette + Pydantic)

**Advantages over Django:**
- Lighter weight, more flexible
- Better async support
- Faster development for APIs
- Modern Python features (type hints)

**Choose FastAPI when:**
- Building APIs (not full-stack web apps)
- Need high performance
- Want automatic documentation
- Prefer type hints

### Q12: Explain FastAPI's dependency injection system
**Answer:**
FastAPI's `Depends()` creates a dependency tree that's resolved at request time.

```python
# Level 1: Database connection
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# Level 2: Service depends on DB
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

# Level 3: Current user depends on service
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: UserService = Depends(get_user_service)
) -> User:
    return await service.get_by_token(token)

# Level 4: Route depends on user
@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return user
```

**Benefits:**
- Loose coupling
- Easy testing (override dependencies)
- Automatic resource cleanup
- Reusable components

### Q13: How does Pydantic validation work in FastAPI?
**Answer:**
Pydantic validates request/response data using Python type hints.

```python
from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    email: EmailStr                              # Built-in email validation
    username: str = Field(..., min_length=3)    # Field constraints
    age: int = Field(ge=0, le=150)              # Range validation
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError("Must be alphanumeric")
        return v.lower()
```

**Validation happens automatically:**
1. Request body parsed to dict
2. Dict passed to Pydantic model
3. Validation rules applied
4. 422 error returned if invalid

### Q14: What is the difference between `Query`, `Path`, `Body`, and `Header`?
**Answer:**
```python
@router.get("/items/{item_id}")
async def get_item(
    # Path parameter
    item_id: int = Path(..., gt=0, description="Item ID"),
    
    # Query parameters
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    search: Optional[str] = Query(None),
    
    # Header
    x_token: str = Header(...),
    
    # Cookie
    session_id: Optional[str] = Cookie(None)
):
    ...

@router.post("/items")
async def create_item(
    # Request body
    item: ItemCreate = Body(..., embed=True)
):
    ...
```

### Q15: How do you handle authentication in FastAPI?
**Answer:**
Using OAuth2 with JWT tokens:

```python
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid token")
    
    user = await user_service.get(user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user
```

### Q16: Explain middleware in FastAPI
**Answer:**
Middleware processes every request/response.

```python
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Before request
        request_id = str(uuid4())
        logger.info(f"Request {request_id}: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # After response
        logger.info(f"Response {request_id}: {response.status_code}")
        
        return response

app.add_middleware(LoggingMiddleware)
```

**Common middleware:**
- CORS
- Authentication
- Rate limiting
- Request logging
- Response compression

### Q17: How do you handle errors in FastAPI?
**Answer:**
```python
# Custom exception
class NotFoundError(Exception):
    def __init__(self, resource: str, id: int):
        self.resource = resource
        self.id = id

# Exception handler
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "not_found",
            "message": f"{exc.resource} with id {exc.id} not found"
        }
    )

# Usage in route
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await user_service.get(user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user
```

### Q18: What are background tasks in FastAPI?
**Answer:**
Tasks that run after the response is sent.

```python
from fastapi import BackgroundTasks

def send_notification(email: str, message: str):
    # This runs after response is sent
    email_service.send(email, message)

@router.post("/orders")
async def create_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks
):
    created_order = await order_service.create(order)
    
    # Schedule background task
    background_tasks.add_task(
        send_notification,
        order.customer_email,
        f"Order {created_order.id} confirmed"
    )
    
    return created_order  # Response sent immediately
```

**Use cases:**
- Email notifications
- Logging to external services
- Cleanup operations
- Non-critical processing

### Q19: How do you implement WebSocket in FastAPI?
**Answer:**
```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Q20: How do you version APIs in FastAPI?
**Answer:**
**URL-based versioning (used in this project):**
```python
# app/api/v1/__init__.py
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(users.router, prefix="/users")
api_v1_router.include_router(tasks.router, prefix="/tasks")

# app/api/v2/__init__.py
api_v2_router = APIRouter(prefix="/api/v2")
api_v2_router.include_router(users_v2.router, prefix="/users")

# app/main.py
app.include_router(api_v1_router)
app.include_router(api_v2_router)
```

**Header-based versioning:**
```python
async def get_api_version(
    api_version: str = Header("v1", alias="X-API-Version")
) -> str:
    return api_version

@router.get("/users")
async def get_users(version: str = Depends(get_api_version)):
    if version == "v2":
        return await get_users_v2()
    return await get_users_v1()
```

---

## Section 3: Database & SQLAlchemy

### Q21: What is SQLAlchemy and how does it work?
**Answer:**
SQLAlchemy is a Python SQL toolkit and ORM.

**Two main components:**
1. **Core**: SQL Expression Language
2. **ORM**: Object-Relational Mapping

```python
# ORM Model
class User(Base):
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String(255), unique=True)

# Core expression
stmt = select(User).where(User.email == "test@example.com")

# Execute
result = await session.execute(stmt)
user = result.scalar_one_or_none()
```

### Q22: Explain SQLAlchemy relationship types
**Answer:**
```python
# One-to-Many
class User(Base):
    projects = relationship("Project", back_populates="owner")

class Project(Base):
    owner_id = mapped_column(ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")

# Many-to-Many
project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id")),
    Column("user_id", ForeignKey("users.id"))
)

class Project(Base):
    members = relationship("User", secondary=project_members)

# One-to-One
class User(Base):
    profile = relationship("Profile", back_populates="user", uselist=False)
```

### Q23: What is the N+1 query problem and how do you solve it?
**Answer:**
**Problem:** Loading related objects in separate queries.

```python
# N+1 problem
users = await session.execute(select(User))
for user in users.scalars():
    # Each iteration makes a new query!
    print(user.projects)  # SELECT * FROM projects WHERE user_id = ?
```

**Solution: Eager loading**
```python
# joinedload (single query with JOIN)
stmt = select(User).options(joinedload(User.projects))
users = await session.execute(stmt)

# selectinload (two queries, better for many results)
stmt = select(User).options(selectinload(User.projects))
users = await session.execute(stmt)
```

### Q24: What are database migrations and why use Alembic?
**Answer:**
Migrations track database schema changes in version control.

**Alembic commands:**
```bash
# Generate migration
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View history
alembic history
```

**Migration file:**
```python
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

def downgrade():
    op.drop_table('users')
```

### Q25: Explain async SQLAlchemy 2.0 patterns
**Answer:**
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Create async engine
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=True
)

# Create session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Usage
async with async_session() as session:
    async with session.begin():
        user = User(email="test@example.com")
        session.add(user)
        # Commits automatically at end of context

# Query patterns
result = await session.execute(select(User).where(User.id == 1))
user = result.scalar_one_or_none()  # Returns User or None
users = result.scalars().all()       # Returns list[User]
```

---

## Section 4: Security

### Q26: How does JWT authentication work?
**Answer:**
JWT (JSON Web Token) consists of three parts: Header, Payload, Signature.

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.rTCH8cLoGxAm_xw68z-zXVKi9ie6xJn9tnP
|_____Header_____|_____Payload_____|___________Signature__________|
```

**Flow:**
1. User logs in with credentials
2. Server validates and creates JWT
3. Client stores JWT and sends with requests
4. Server validates JWT on each request

```python
# Create token
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# Validate token
def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

### Q27: What is RBAC (Role-Based Access Control)?
**Answer:**
RBAC restricts system access based on user roles.

**Implementation:**
```python
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(403, "Insufficient permissions")
        return user

# Usage
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(RoleChecker([UserRole.ADMIN]))
):
    await user_service.delete(user_id)
```

### Q28: How do you prevent SQL injection?
**Answer:**
**SQLAlchemy ORM prevents SQL injection automatically:**
```python
# Safe - parameterized query
user_input = "'; DROP TABLE users; --"
stmt = select(User).where(User.username == user_input)
# Generates: SELECT * FROM users WHERE username = $1
# Parameter: "'; DROP TABLE users; --"

# Dangerous - never do this!
query = f"SELECT * FROM users WHERE username = '{user_input}'"
```

### Q29: Explain password hashing best practices
**Answer:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Work factor
)

# Hash password (includes salt automatically)
hashed = pwd_context.hash("plaintext")
# Result: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtLHAkCOYz6

# Verify password
is_valid = pwd_context.verify("plaintext", hashed)
```

**Best practices:**
- Use bcrypt/argon2 (not MD5/SHA1)
- Use random salt (bcrypt does this automatically)
- Use appropriate work factor (12+ for bcrypt)
- Never store plaintext passwords
- Never log passwords

### Q30: What security headers should an API implement?
**Answer:**
```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HTTPS enforcement
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
```

---

## Section 5: Testing

### Q31: What testing strategies do you use for APIs?
**Answer:**
**Testing pyramid:**
1. **Unit tests**: Individual functions, 70%
2. **Integration tests**: API endpoints, 20%
3. **E2E tests**: Full flows, 10%

```python
# Unit test
@pytest.mark.asyncio
async def test_create_user_service(user_service, user_data):
    user = await user_service.create_user(user_data)
    assert user.email == user_data.email

# Integration test
@pytest.mark.asyncio
async def test_create_user_endpoint(client, auth_headers):
    response = await client.post("/api/v1/users", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "Password123"
    }, headers=auth_headers)
    assert response.status_code == 201
```

### Q32: How do you test async code with pytest?
**Answer:**
```python
import pytest
from httpx import AsyncClient

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_get_users(client):
    response = await client.get("/api/v1/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

**pytest.ini configuration:**
```ini
[pytest]
asyncio_mode = auto
```

### Q33: How do you mock database in tests?
**Answer:**
```python
@pytest.fixture
async def test_db():
    # Create in-memory SQLite database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def app_with_test_db(test_db):
    # Override dependency
    app.dependency_overrides[get_db] = lambda: test_db
    yield app
    app.dependency_overrides.clear()
```

### Q34: What is test coverage and how do you measure it?
**Answer:**
Test coverage measures which code is executed during tests.

```bash
# Run with coverage
pytest --cov=app --cov-report=html

# Output
Name                      Stmts   Miss  Cover
---------------------------------------------
app/services/user.py        50      5    90%
app/api/v1/users.py         30      2    93%
---------------------------------------------
TOTAL                      200     20    90%
```

**Coverage types:**
- Line coverage: % of lines executed
- Branch coverage: % of branches taken
- Path coverage: % of execution paths

**Target:** 80%+ coverage, but focus on critical paths

---

## Section 6: Architecture & Design

### Q35: What is the Repository Pattern?
**Answer:**
Separates data access logic from business logic.

```python
# Repository (data access)
class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get(self, id: int) -> Optional[User]:
        return await self.db.get(User, id)
    
    async def create(self, data: dict) -> User:
        user = User(**data)
        self.db.add(user)
        await self.db.commit()
        return user

# Service (business logic)
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    async def create_user(self, data: UserCreate) -> User:
        # Business logic: validate, hash password
        if await self.repository.get_by_email(data.email):
            raise ValidationError("Email already exists")
        
        hashed_password = hash_password(data.password)
        return await self.repository.create({
            **data.model_dump(exclude={"password"}),
            "hashed_password": hashed_password
        })
```

**Benefits:**
- Testability (mock repository)
- Flexibility (swap database)
- Separation of concerns

### Q36: What is Dependency Injection and why is it important?
**Answer:**
DI provides dependencies to objects rather than having them create their own.

**Without DI:**
```python
class UserService:
    def __init__(self):
        self.db = Database()  # Hard-coded dependency
```

**With DI:**
```python
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db  # Injected dependency

# In FastAPI
async def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)
```

**Benefits:**
- Testability: Inject mock dependencies
- Flexibility: Change implementations
- Loose coupling: Services don't know about construction

### Q37: How do you handle configuration in different environments?
**Answer:**
Using Pydantic Settings with environment variables:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    DATABASE_URL: str
    SECRET_KEY: str
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

# Different .env files
# .env.development
DEBUG=true
DATABASE_URL=sqlite:///./dev.db

# .env.production
DEBUG=false
DATABASE_URL=postgresql://user:pass@db:5432/prod
```

### Q38: What is the difference between sync and async programming?
**Answer:**
**Synchronous:** Blocks until operation completes
```python
def get_data():
    response = requests.get(url)  # Blocks here
    return response.json()
```

**Asynchronous:** Releases control while waiting
```python
async def get_data():
    response = await httpx.get(url)  # Releases control
    return response.json()
```

**When to use async:**
- I/O-bound operations (database, HTTP)
- Many concurrent connections
- Real-time applications

**Performance comparison:**
- 1000 sync requests: ~30 seconds (sequential)
- 1000 async requests: ~2 seconds (concurrent)

### Q39: How do you structure a large FastAPI project?
**Answer:**
```
project/
├── app/
│   ├── main.py           # Application factory
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py    # Router aggregation
│   │       └── endpoints/     # Route handlers
│   ├── core/             # Configuration, security
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── dependencies/     # DI providers
│   └── utils/            # Helpers, middleware
├── tests/
├── alembic/
└── docker/
```

**Key principles:**
- Separate by feature, not by type
- Keep routes thin, logic in services
- Use dependency injection
- Version APIs from the start

### Q40: How do you handle database transactions?
**Answer:**
```python
# Automatic transaction management
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# Manual transaction control
async def transfer_funds(from_id: int, to_id: int, amount: float):
    async with async_session() as session:
        async with session.begin():  # Start transaction
            from_account = await session.get(Account, from_id)
            to_account = await session.get(Account, to_id)
            
            if from_account.balance < amount:
                raise ValueError("Insufficient funds")
            
            from_account.balance -= amount
            to_account.balance += amount
            # Commits when context exits, rolls back on exception
```

---

## Section 7: DevOps & Deployment

### Q41: How do you containerize a Python application?
**Answer:**
**Multi-stage Dockerfile:**
```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Production stage
FROM python:3.11-slim
WORKDIR /app

# Install dependencies from wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application
COPY app/ ./app/

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Best practices:**
- Use multi-stage builds (smaller images)
- Don't run as root
- Use `.dockerignore`
- Pin dependency versions

### Q42: What is Docker Compose and how do you use it?
**Answer:**
Docker Compose orchestrates multi-container applications.

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/app
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./app:/app/app  # Hot reload in development

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Q43: How do you implement health checks?
**Answer:**
```python
@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        raise HTTPException(503, detail={"status": "not ready", "error": str(e)})

@router.get("/health/live")
async def liveness_check():
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
```

**Kubernetes usage:**
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Q44: What is CI/CD and how would you set it up?
**Answer:**
**GitHub Actions example:**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest --cov=app
        env:
          DATABASE_URL: postgresql://postgres:test@localhost/postgres
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to production
        run: |
          # Deploy commands
```

### Q45: How do you monitor a FastAPI application in production?
**Answer:**
**Structured logging:**
```python
import structlog

logger = structlog.get_logger()

@router.get("/users/{user_id}")
async def get_user(user_id: int, request: Request):
    logger.info(
        "Fetching user",
        user_id=user_id,
        request_id=request.headers.get("X-Request-ID"),
        path=request.url.path
    )
```

**Metrics with Prometheus:**
```python
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(time.time() - start_time)
    
    return response
```

---

## Section 8: Problem Solving

### Q46: How would you implement rate limiting?
**Answer:**
```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[float]] = defaultdict(list)
    
    def is_allowed(self, key: str) -> bool:
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[key] = [
            t for t in self.requests[key] if t > minute_ago
        ]
        
        if len(self.requests[key]) >= self.requests_per_minute:
            return False
        
        self.requests[key].append(now)
        return True

rate_limiter = RateLimiter(60)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"}
        )
    
    return await call_next(request)
```

### Q47: How would you implement pagination?
**Answer:**
```python
class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100)
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

async def paginate(
    query: Select,
    session: AsyncSession,
    params: PaginationParams
) -> PaginatedResponse:
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query)
    
    # Get paginated items
    paginated_query = query.offset(params.offset).limit(params.page_size)
    result = await session.execute(paginated_query)
    items = result.scalars().all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size
    )
```

### Q48: How would you implement soft delete?
**Answer:**
```python
class SoftDeleteMixin:
    deleted_at: Mapped[Optional[datetime]] = mapped_column(default=None)
    
    @hybrid_property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
    
    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        self.deleted_at = None

class User(Base, SoftDeleteMixin):
    # ...

# Repository with soft delete filter
class UserRepository:
    async def get_active(self, id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .where(User.id == id)
            .where(User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()
    
    async def soft_delete(self, id: int) -> None:
        user = await self.get_active(id)
        if user:
            user.soft_delete()
            await self.db.commit()
```

### Q49: How would you handle file uploads securely?
**Answer:**
```python
import aiofiles
from uuid import uuid4

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_file(file: UploadFile) -> None:
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "File type not allowed")
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")
    
    await file.seek(0)  # Reset file pointer

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    await validate_file(file)
    
    # Generate unique filename
    ext = Path(file.filename).suffix
    unique_name = f"{uuid4()}{ext}"
    file_path = f"uploads/{user.id}/{unique_name}"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    return {"filename": unique_name, "path": file_path}
```

### Q50: How do you optimize database queries?
**Answer:**
**1. Use indexes:**
```python
class User(Base):
    email = mapped_column(String, unique=True, index=True)
    username = mapped_column(String, index=True)
```

**2. Eager loading:**
```python
# Instead of lazy loading (N+1)
stmt = select(User).options(
    selectinload(User.projects),
    selectinload(User.tasks)
)
```

**3. Select only needed columns:**
```python
# Instead of selecting all columns
stmt = select(User.id, User.email, User.username)
```

**4. Use pagination:**
```python
stmt = select(User).offset(0).limit(20)
```

**5. Database-level aggregations:**
```python
# Instead of fetching all and counting in Python
stmt = select(func.count(Task.id)).where(Task.status == "done")
```

**6. Connection pooling:**
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)
```

---

## Bonus Questions

### Q51: How do you handle secrets in production?
**Answer:**
- Never commit secrets to version control
- Use environment variables
- Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- Use `.env` files only for development
- Rotate secrets regularly

### Q52: What's the difference between authentication and authorization?
**Answer:**
- **Authentication**: Verifying identity (Who are you?)
- **Authorization**: Verifying permissions (What can you do?)

### Q53: How do you ensure API backward compatibility?
**Answer:**
- Use API versioning (`/api/v1/`, `/api/v2/`)
- Add new fields as optional
- Never remove fields without deprecation period
- Document breaking changes

### Q54: What is CORS and why is it important?
**Answer:**
CORS (Cross-Origin Resource Sharing) controls which domains can access your API from a browser. Without proper CORS configuration, browsers will block requests from different origins.

### Q55: How do you handle long-running tasks?
**Answer:**
- Use background tasks for simple cases
- Use task queues (Celery, RQ) for complex workflows
- Implement progress tracking
- Return task ID for status polling

---

# Summary

This comprehensive guide covers the Task Management API project built with FastAPI, demonstrating:

**Python Mastery:**
- OOP principles and design patterns
- Type hints and generics
- Async/await programming
- Decorators and context managers
- Exception handling best practices

**FastAPI Expertise:**
- Dependency injection
- Pydantic validation
- Authentication/Authorization
- WebSocket support
- Middleware implementation

**Database Skills:**
- SQLAlchemy 2.0 async patterns
- Alembic migrations
- Query optimization
- Repository pattern

**DevOps Practices:**
- Docker containerization
- CI/CD pipelines
- Testing strategies
- Production monitoring

**Security Implementation:**
- JWT authentication
- Role-based access control
- Password hashing
- Security headers

This project serves as both a learning resource and a production-ready template for building FastAPI applications.

---

*Document Version: 1.0*
*Last Updated: April 2026*
*Author: Development Team*
