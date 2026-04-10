"""API v1 router combining all endpoint modules."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    projects,
    tasks,
    health,
    websocket,
    files,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["Projects"]
)

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Tasks"]
)

api_router.include_router(
    files.router,
    prefix="/files",
    tags=["Files"]
)

api_router.include_router(
    websocket.router,
    prefix="/ws",
    tags=["WebSocket"]
)
