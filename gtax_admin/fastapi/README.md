# Task Management API

A production-ready FastAPI application demonstrating comprehensive usage of Python and FastAPI best practices.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

### Core Features
- **JWT Authentication** - Secure authentication with access and refresh tokens
- **Role-Based Authorization** - Admin, Manager, and User roles with permissions
- **Task Management** - Create, assign, track, and manage tasks
- **Project Management** - Organize tasks into projects
- **Real-time Updates** - WebSocket support for live notifications

### Technical Features
- **Async/Await** - Fully asynchronous API with SQLAlchemy 2.0
- **Type Hints** - Complete type annotations throughout
- **Dependency Injection** - Clean dependency management with FastAPI
- **Repository Pattern** - Clean separation of data access layer
- **Database Migrations** - Alembic for schema management
- **Comprehensive Testing** - Pytest with async support

### DevOps Features
- **Docker Support** - Multi-stage Dockerfile for dev/prod
- **Docker Compose** - Full development environment
- **Pre-commit Hooks** - Automated code quality checks
- **Structured Logging** - JSON logging for production

## 📁 Project Structure

```
fastapi/
├── app/
│   ├── main.py              # Application entry point
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/   # API route handlers
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── projects.py
│   │   │   │   ├── tasks.py
│   │   │   │   ├── files.py
│   │   │   │   ├── websocket.py
│   │   │   │   └── health.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py        # Settings management
│   │   ├── security.py      # JWT & password hashing
│   │   ├── logging.py       # Structured logging
│   │   └── exceptions.py    # Custom exceptions
│   ├── models/
│   │   ├── user.py          # User model
│   │   ├── project.py       # Project model
│   │   ├── task.py          # Task model
│   │   └── base.py          # Base mixins
│   ├── schemas/
│   │   ├── user.py          # User Pydantic schemas
│   │   ├── project.py       # Project schemas
│   │   ├── task.py          # Task schemas
│   │   └── common.py        # Shared schemas
│   ├── services/
│   │   ├── user_service.py  # User business logic
│   │   ├── project_service.py
│   │   ├── task_service.py
│   │   ├── auth_service.py
│   │   └── base.py          # Base repository
│   ├── dependencies/
│   │   ├── auth.py          # Auth dependencies
│   │   ├── pagination.py    # Pagination helpers
│   │   └── services.py      # Service factories
│   ├── db/
│   │   └── database.py      # Database configuration
│   └── utils/
│       ├── middleware.py    # Custom middleware
│       ├── helpers.py       # Utility functions
│       └── decorators.py    # Custom decorators
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── test_auth_api.py     # Auth endpoint tests
│   ├── test_api.py          # API integration tests
│   └── test_user_service.py # Service unit tests
├── alembic/
│   ├── env.py               # Alembic configuration
│   └── versions/            # Migration files
├── scripts/
│   └── init-db.sql          # Database init script
├── requirements.txt         # Python dependencies
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Development environment
├── docker-compose.prod.yml  # Production environment
├── .env.example             # Environment template
├── .pre-commit-config.yaml  # Pre-commit hooks
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- PostgreSQL (or SQLite for development)
- Redis (optional, for caching)

### Local Development

1. **Clone the repository**
   ```bash
   cd fastapi
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Development

1. **Start all services**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f api
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

## 📖 API Documentation

### Authentication

All protected endpoints require a JWT token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=SecurePass123
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Projects

#### Create Project
```http
POST /api/v1/projects
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Project",
  "description": "Project description"
}
```

#### List Projects
```http
GET /api/v1/projects?page=1&page_size=20&status=active
Authorization: Bearer <token>
```

### Tasks

#### Create Task
```http
POST /api/v1/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Implement feature",
  "description": "Detailed description",
  "project_id": 1,
  "priority": "high",
  "due_date": "2025-12-31T23:59:59Z"
}
```

#### List Tasks with Filters
```http
GET /api/v1/tasks?project_id=1&status=todo&priority=high&sort_by=due_date&sort_order=asc
Authorization: Bearer <token>
```

#### Change Task Status
```http
PATCH /api/v1/tasks/1/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "in_progress"
}
```

### WebSocket

Connect to receive real-time updates:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/connect?token=<jwt_token>');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

// Send message
ws.send(JSON.stringify({
  type: 'join_room',
  room: 'project-1'
}));
```

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run Specific Tests
```bash
# Unit tests only
pytest tests/test_user_service.py

# Integration tests
pytest tests/test_api.py

# With verbose output
pytest -v
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./task_management.db` |
| `SECRET_KEY` | JWT secret key | (required) |
| `DEBUG` | Debug mode | `False` |
| `ENVIRONMENT` | Environment name | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ALLOWED_ORIGINS` | CORS origins (comma-separated) | `http://localhost:3000` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token expiry | `30` |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `60` |

## 📦 Database Migrations

### Create Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback
```bash
alembic downgrade -1
```

## 🎯 Python Concepts Demonstrated

1. **OOP Principles**
   - Classes and inheritance (`BaseRepository`, model mixins)
   - Encapsulation (service layer)
   - Polymorphism (exception handling)

2. **Type Hints**
   - Function annotations
   - Generic types (`TypeVar`, `Generic`)
   - `Annotated` for dependency injection

3. **Decorators**
   - Custom decorators (`@log_execution`, `@retry`)
   - FastAPI decorators (`@router.get`, `@app.middleware`)

4. **Context Managers**
   - Database sessions (`async with`)
   - Logging context (`LoggingContext`)

5. **Async Programming**
   - `async/await` throughout
   - Async database operations
   - Background tasks

## 🔒 Security Features

- **Password Hashing**: bcrypt with automatic salt
- **JWT Tokens**: Access + refresh token pattern
- **Rate Limiting**: IP-based request limiting
- **Input Validation**: Pydantic schemas with constraints
- **CORS**: Configurable allowed origins
- **SQL Injection Protection**: SQLAlchemy ORM

## 📊 Performance Considerations

- **Connection Pooling**: SQLAlchemy pool configuration
- **Async Operations**: Non-blocking I/O
- **Pagination**: All list endpoints paginated
- **Selective Loading**: SQLAlchemy `selectinload`
- **Caching Ready**: Redis integration prepared

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 💬 Support

For support, please open an issue in the GitHub repository.
