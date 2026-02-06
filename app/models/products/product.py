"""Product domain model."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Product(BaseModel):
    """Product model representing catalog items."""
    
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    category: str
    unit: str
    business_unit: str
    location: str
    price: float
    is_available: bool = True
    product_type: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
