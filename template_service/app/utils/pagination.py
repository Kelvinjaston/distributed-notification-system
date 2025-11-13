"""
Pagination utilities.
"""
from typing import Generic, TypeVar, List, Dict, Any
from pydantic import BaseModel

T = TypeVar('T')


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    total: int
    limit: int
    page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    data: List[T]
    meta: PaginationMeta


def calculate_pagination_meta(
    total: int,
    page: int,
    limit: int
) -> PaginationMeta:
    """Calculate pagination metadata."""
    total_pages = (total + limit - 1) // limit  # Ceiling division
    has_next = page < total_pages
    has_previous = page > 1

    return PaginationMeta(
        total=total,
        limit=limit,
        page=page,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous
    )
