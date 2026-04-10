"""
Custom exception classes and exception handlers.

Demonstrates:
- Exception inheritance hierarchy
- Custom exception attributes
- Exception handler registration
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class BaseAppException(Exception):
    """
    Base exception class for all application exceptions.
    
    Demonstrates:
    - Exception inheritance
    - Custom attributes for error details
    - String representation override
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize base exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code or "APP_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """String representation of the exception."""
        return f"[{self.error_code}] {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class NotFoundError(BaseAppException):
    """Exception raised when a resource is not found."""
    
    def __init__(
        self,
        resource: str,
        identifier: Any,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize not found error.
        
        Args:
            resource: Name of the resource (e.g., "User", "Task")
            identifier: The identifier that was not found
            details: Additional error details
        """
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            details=details or {"resource": resource, "identifier": str(identifier)}
        )


class ValidationError(BaseAppException):
    """Exception raised for validation errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize validation error.
        
        Args:
            message: Validation error message
            field: The field that failed validation
            details: Additional error details
        """
        error_details = details or {}
        if field:
            error_details["field"] = field
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=error_details
        )


class AuthenticationError(BaseAppException):
    """Exception raised for authentication failures."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize authentication error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            details=details
        )


class AuthorizationError(BaseAppException):
    """Exception raised for authorization failures."""
    
    def __init__(
        self,
        message: str = "You don't have permission to perform this action",
        required_permission: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize authorization error.
        
        Args:
            message: Error message
            required_permission: The permission that was required
            details: Additional error details
        """
        error_details = details or {}
        if required_permission:
            error_details["required_permission"] = required_permission
        
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            details=error_details
        )


class ConflictError(BaseAppException):
    """Exception raised for resource conflicts (e.g., duplicate entries)."""
    
    def __init__(
        self,
        message: str,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize conflict error.
        
        Args:
            message: Error message
            resource: The conflicting resource type
            details: Additional error details
        """
        error_details = details or {}
        if resource:
            error_details["resource"] = resource
        
        super().__init__(
            message=message,
            error_code="CONFLICT",
            details=error_details
        )


class RateLimitError(BaseAppException):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Seconds until retry is allowed
            details: Additional error details
        """
        error_details = details or {}
        if retry_after:
            error_details["retry_after"] = retry_after
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=error_details
        )


class DatabaseError(BaseAppException):
    """Exception raised for database errors."""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize database error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details
        )


# Exception to HTTP status code mapping
EXCEPTION_STATUS_MAP = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ValidationError: status.HTTP_400_BAD_REQUEST,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    ConflictError: status.HTTP_409_CONFLICT,
    RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
    DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


async def app_exception_handler(
    request: Request,
    exc: BaseAppException
) -> JSONResponse:
    """
    Global exception handler for application exceptions.
    
    Args:
        request: The incoming request
        exc: The raised exception
        
    Returns:
        JSONResponse: Formatted error response
    """
    status_code = EXCEPTION_STATUS_MAP.get(
        type(exc),
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    return JSONResponse(
        status_code=status_code,
        content=exc.to_dict()
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """
    Handler for FastAPI HTTPException.
    
    Args:
        request: The incoming request
        exc: The raised HTTPException
        
    Returns:
        JSONResponse: Formatted error response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": "HTTP_ERROR",
            "message": exc.detail,
            "details": {}
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handler for unhandled exceptions.
    
    Args:
        request: The incoming request
        exc: The raised exception
        
    Returns:
        JSONResponse: Generic error response
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": {}
        }
    )
