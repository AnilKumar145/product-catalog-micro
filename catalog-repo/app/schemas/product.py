"""Product schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Base product schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: str
    unit: str
    business_unit: str
    location: str
    price: float = Field(..., gt=0)
    product_type: str = Field(..., pattern="^(HW|SW)$")


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = None
    unit: Optional[str] = None
    business_unit: Optional[str] = None
    location: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    product_type: Optional[str] = Field(None, pattern="^(HW|SW)$")
    is_available: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product response."""
    id: int
    is_available: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PriceUpdate(BaseModel):
    """Schema for updating product price."""
    price: float = Field(..., gt=0)


class AvailabilityUpdate(BaseModel):
    """Schema for updating product availability."""
    is_available: bool
