"""
Pagination dependency for list endpoints.

Demonstrates:
- Query parameter validation
- Reusable pagination logic
- Type annotations with Annotated
"""

from typing import Annotated

from fastapi import Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    """Pagination parameters model."""
    
    page: int
    page_size: int
    sort_by: str | None
    sort_order: str
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database query."""
        return self.page_size


async def get_pagination(
    page: Annotated[
        int,
        Query(
            ge=1,
            description="Page number (1-indexed)",
            examples=[1]
        )
    ] = 1,
    page_size: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Number of items per page",
            examples=[20]
        )
    ] = 20,
    sort_by: Annotated[
        str | None,
        Query(
            description="Field to sort by",
            examples=["created_at", "name"]
        )
    ] = None,
    sort_order: Annotated[
        str,
        Query(
            pattern="^(asc|desc)$",
            description="Sort order (asc or desc)",
            examples=["desc"]
        )
    ] = "desc"
) -> PaginationParams:
    """
    Extract and validate pagination parameters from query string.
    
    This dependency can be used in any list endpoint to provide
    consistent pagination behavior.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        sort_by: Optional field to sort by
        sort_order: Sort direction (asc or desc)
        
    Returns:
        PaginationParams: Validated pagination parameters
        
    Example:
        >>> @router.get("/items")
        ... async def list_items(
        ...     pagination: PaginationParams = Depends(get_pagination)
        ... ):
        ...     items = await service.get_items(
        ...         skip=pagination.offset,
        ...         limit=pagination.limit
        ...     )
    """
    return PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )


# Type alias for easier dependency injection
PaginationDep = Annotated[PaginationParams, Query()]
