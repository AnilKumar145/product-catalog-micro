"""Product domain model."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class Product(BaseModel):
    """Product model representing catalog items."""
    
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    
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
