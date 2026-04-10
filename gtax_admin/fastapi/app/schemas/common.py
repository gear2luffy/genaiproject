"""
Common Pydantic schemas used across the application.

Demonstrates:
- Generic response models
- Pagination support
- Health check responses
"""

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# Generic type for paginated items
T = TypeVar("T")


class BaseSchema(BaseModel):
    """
    Base schema with common configuration.
    
    All schemas should inherit from this for consistent behavior.
    """
    
    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode
        str_strip_whitespace=True,  # Strip whitespace from strings
        validate_assignment=True,  # Validate on attribute assignment
    )


class PaginationParams(BaseModel):
    """
    Pagination parameters for list endpoints.
    
    Example:
        GET /api/v1/tasks?page=1&page_size=20&sort_by=created_at&sort_order=desc
    """
    
    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-indexed)"
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page"
    )
    sort_by: Optional[str] = Field(
        default=None,
        description="Field to sort by"
    )
    sort_order: str = Field(
        default="asc",
        pattern="^(asc|desc)$",
        description="Sort order (asc or desc)"
    )
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database query."""
        return self.page_size


class PaginatedResponse(BaseSchema, Generic[T]):
    """
    Generic paginated response wrapper.
    
    Demonstrates:
    - Generic type support in Pydantic
    - Pagination metadata
    """
    
    items: List[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """
        Factory method to create paginated response.
        
        Args:
            items: List of items for current page
            total: Total number of items
            page: Current page number
            page_size: Number of items per page
            
        Returns:
            PaginatedResponse: Populated pagination response
        """
        pages = (total + page_size - 1) // page_size if total > 0 else 1
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )


class MessageResponse(BaseSchema):
    """Simple message response for operations."""
    
    message: str = Field(description="Response message")
    success: bool = Field(default=True, description="Operation success status")
    data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional additional data"
    )


class ErrorResponse(BaseSchema):
    """Error response schema."""
    
    error_code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional error details"
    )


class HealthResponse(BaseSchema):
    """Health check response schema."""
    
    status: str = Field(description="Service status (healthy/unhealthy)")
    version: str = Field(description="Application version")
    environment: str = Field(description="Environment name")
    timestamp: datetime = Field(description="Check timestamp")
    services: dict[str, str] = Field(
        default_factory=dict,
        description="Status of dependent services"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "development",
                "timestamp": "2025-01-01T00:00:00Z",
                "services": {
                    "database": "connected",
                    "redis": "connected"
                }
            }
        }


class FilterParams(BaseModel):
    """Common filter parameters for list endpoints."""
    
    search: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Search query string"
    )
    created_after: Optional[datetime] = Field(
        default=None,
        description="Filter items created after this date"
    )
    created_before: Optional[datetime] = Field(
        default=None,
        description="Filter items created before this date"
    )
