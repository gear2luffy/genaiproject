"""
Custom middleware implementations.

Demonstrates:
- Request logging middleware
- Timing/performance middleware
- Rate limiting middleware
- ASGI middleware pattern
"""

import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import settings
from app.core.logging import get_logger, request_context

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all HTTP requests and responses.
    
    Demonstrates:
    - Request/response logging
    - Request ID generation
    - Context management for logging
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process request with logging.
        
        Args:
            request: The incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response: The response
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Set context for logging
        token = request_context.set({
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method
        })
        
        # Add request ID to response headers
        start_time = time.perf_counter()
        
        try:
            # Log request
            logger.info(
                "Request started",
                method=request.method,
                path=request.url.path,
                query=str(request.query_params),
                client_ip=request.client.host if request.client else "unknown"
            )
            
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Log response
            logger.info(
                "Request completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2)
            )
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            
            return response
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "Request failed",
                error=str(e),
                duration_ms=round(duration_ms, 2)
            )
            raise
        
        finally:
            request_context.reset(token)


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking request timing.
    
    Simpler alternative to full logging middleware,
    just adds timing headers.
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """Add timing headers to response."""
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
        
        # Log slow requests
        if duration_ms > 1000:  # > 1 second
            logger.warning(
                "Slow request detected",
                path=request.url.path,
                duration_ms=round(duration_ms, 2)
            )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    
    Demonstrates:
    - Rate limiting implementation
    - Token bucket algorithm concept
    - IP-based limiting
    
    Note: For production, use Redis-based rate limiting
    for distributed systems.
    """
    
    def __init__(
        self,
        app,
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> None:
        """
        Initialize rate limiter.
        
        Args:
            app: The ASGI application
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        
        # Store: {client_ip: [(timestamp, count)]}
        self._requests: Dict[str, list] = defaultdict(list)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for forwarded headers (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self, client_ip: str, now: datetime) -> None:
        """Remove requests outside the current window."""
        cutoff = now - timedelta(seconds=self.window_seconds)
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip]
            if ts > cutoff
        ]
    
    def _is_rate_limited(self, client_ip: str) -> tuple[bool, int]:
        """
        Check if client is rate limited.
        
        Returns:
            Tuple of (is_limited, remaining_requests)
        """
        now = datetime.utcnow()
        
        # Clean up old requests
        self._cleanup_old_requests(client_ip, now)
        
        # Count requests in current window
        request_count = len(self._requests[client_ip])
        remaining = max(0, self.max_requests - request_count)
        
        if request_count >= self.max_requests:
            return True, 0
        
        # Record this request
        self._requests[client_ip].append(now)
        
        return False, remaining - 1
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Check rate limit and process request.
        
        Args:
            request: The incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response: The response or 429 error
        """
        # Skip rate limiting for certain paths
        skip_paths = ["/api/v1/health", "/docs", "/openapi.json"]
        if request.url.path in skip_paths:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        is_limited, remaining = self._is_rate_limited(client_ip)
        
        if is_limited:
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                path=request.url.path
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "details": {
                        "retry_after": self.window_seconds
                    }
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(self.window_seconds)
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response


class CORSDebugMiddleware(BaseHTTPMiddleware):
    """
    Debug middleware for logging CORS requests.
    
    Useful during development to debug CORS issues.
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """Log CORS-related request info."""
        # Log preflight requests
        if request.method == "OPTIONS":
            logger.debug(
                "CORS preflight request",
                origin=request.headers.get("origin"),
                method=request.headers.get("access-control-request-method"),
                headers=request.headers.get("access-control-request-headers")
            )
        
        response = await call_next(request)
        return response
