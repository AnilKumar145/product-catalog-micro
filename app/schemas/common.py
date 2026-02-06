"""Common schemas used across the application."""

from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
