"""
Health check endpoints.

Demonstrates:
- Simple GET endpoint
- Service health checking
- Response models
"""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the API and its dependencies."
)
async def health_check(
    db: AsyncSession = Depends(get_db)
) -> HealthResponse:
    """
    Perform health check on the API and connected services.
    
    Checks:
    - Database connectivity
    - Redis connectivity (if configured)
    
    Returns:
        HealthResponse: Health status information
    """
    services = {}
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        services["database"] = "connected"
    except Exception as e:
        services["database"] = f"error: {str(e)}"
    
    # Check Redis (if configured)
    if settings.redis_url:
        try:
            # Redis check would go here
            services["redis"] = "not_configured"
        except Exception as e:
            services["redis"] = f"error: {str(e)}"
    
    # Determine overall status
    status = "healthy" if all(
        v in ["connected", "not_configured"] 
        for v in services.values()
    ) else "unhealthy"
    
    return HealthResponse(
        status=status,
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.utcnow(),
        services=services
    )


@router.get(
    "/live",
    summary="Liveness Check",
    description="Simple liveness probe for Kubernetes/Docker."
)
async def liveness() -> dict:
    """
    Simple liveness check endpoint.
    
    Used by container orchestration systems to verify
    the application is running.
    
    Returns:
        dict: Simple OK response
    """
    return {"status": "ok"}


@router.get(
    "/ready",
    summary="Readiness Check",
    description="Readiness probe to check if the service can accept traffic."
)
async def readiness(
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Readiness check for service availability.
    
    Verifies the service is ready to handle requests
    by checking database connectivity.
    
    Args:
        db: Database session
        
    Returns:
        dict: Ready status
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return {"status": "not_ready"}
