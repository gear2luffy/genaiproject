"""
Task Management API - Main Application Entry Point

This is a production-ready FastAPI application demonstrating comprehensive
usage of Python and FastAPI concepts.

Run with: uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

from app.api import api_router
from app.core.config import settings
from app.core.logging import get_logger, configure_logging
from app.core.exceptions import (
    BaseAppException,
    app_exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from app.db.database import init_db, close_db
from app.utils.middleware import (
    RequestLoggingMiddleware,
    RateLimitMiddleware,
)

# Configure logging
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the application.
    
    Demonstrates:
    - Async context manager for lifecycle management
    - Database initialization
    - Resource cleanup
    
    Args:
        app: The FastAPI application instance
        
    Yields:
        None
    """
    # Startup
    logger.info(
        "Starting application",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment
    )
    
    # Initialize database tables
    await init_db()
    logger.info("Database initialized")
    
    # Create upload directory
    import os
    os.makedirs(settings.upload_dir, exist_ok=True)
    logger.info("Upload directory ready", path=settings.upload_dir)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    logger.info("Database connections closed")


def create_application() -> FastAPI:
    """
    Application factory function.
    
    Creates and configures the FastAPI application instance.
    
    Demonstrates:
    - Application factory pattern
    - Middleware configuration
    - Exception handlers registration
    - Router inclusion
    
    Returns:
        FastAPI: Configured application instance
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="""
## Task Management API

A production-ready FastAPI application demonstrating comprehensive usage 
of Python and FastAPI best practices.

### Features

- **Authentication**: JWT-based authentication with access and refresh tokens
- **Authorization**: Role-based access control (Admin, Manager, User)
- **Projects**: Create and manage projects
- **Tasks**: Create, assign, and track tasks
- **Real-time**: WebSocket support for live updates
- **Files**: Upload and download file attachments

### Authentication

1. Register a new account using `/api/v1/auth/register`
2. Login using `/api/v1/auth/login` to get tokens
3. Use the access token in the `Authorization` header: `Bearer <token>`

### Rate Limiting

API requests are rate limited to 60 requests per minute per IP address.
        """,
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        },
        contact={
            "name": "API Support",
            "email": "support@example.com"
        }
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    if settings.is_production:
        # Rate limiting in production
        app.add_middleware(
            RateLimitMiddleware,
            max_requests=settings.rate_limit_per_minute,
            window_seconds=60
        )
    
    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Register exception handlers
    app.add_exception_handler(BaseAppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # Include API routers
    app.include_router(api_router, prefix="/api")
    
    return app


# Create application instance
app = create_application()


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    Root endpoint returning API information.
    
    Returns:
        dict: API information
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else "Disabled in production",
        "health": "/api/v1/health"
    }


# Custom OpenAPI schema (optional customization)
def custom_openapi():
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token"
        }
    }
    
    # Apply security globally
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Serve documentation in production with authentication (optional)
if settings.is_production:
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui():
        """Serve Swagger UI with custom configuration."""
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=f"{settings.app_name} - Docs",
            oauth2_redirect_url="/docs/oauth2-redirect",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        )
    
    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc():
        """Serve ReDoc with custom configuration."""
        return get_redoc_html(
            openapi_url="/openapi.json",
            title=f"{settings.app_name} - ReDoc",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js",
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.workers
    )
