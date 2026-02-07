"""Product API endpoints."""

from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from app.schemas.products import (
    ProductCreate, ProductResponse, PriceUpdate, AvailabilityUpdate
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.products import ProductService
from app.models.products import Product
from app.dependencies import require_admin
from app.repositories.products import ProductRepository
from app.infrastructure.cache.redis_cache import RedisCache, get_cache
from app.infrastructure.database.connection import get_db, Database


router = APIRouter(prefix="/products", tags=["Products"])


async def get_product_service(
    db: Database = Depends(get_db),
    cache: RedisCache = Depends(get_cache)
) -> ProductService:
    """Get product service instance."""
    repository = ProductRepository(db)
    return ProductService(repository, cache)


@router.get("", response_model=PaginatedResponse[ProductResponse])
async def get_all_products(
    product_type: Optional[str] = Query(None, description="Filter by HW or SW"),
    business_unit: Optional[str] = Query(None, description="Filter by business unit"),
    location: Optional[str] = Query(None, description="Filter by location"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_by: str = Query("id", description="Sort by field"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: ProductService = Depends(get_product_service)
):
    """Get all products with optional filters and sorting."""
    products, total = await service.get_all_products(
        product_type=product_type,
        business_unit=business_unit,
        location=location,
        category=category,
        sort_by=sort_by,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": [p.model_dump() for p in products],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """Get a specific product by ID."""
    return await service.get_product_by_id(product_id)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service),
    admin: dict = Depends(require_admin)
):
    """Add a new product to the catalog. Requires admin role."""
    product = Product(**product_data.model_dump())
    return await service.create_product(product, admin.get("user_id"))


@router.patch("/{product_id}/price", response_model=ProductResponse)
async def update_product_price(
    product_id: int,
    price_data: PriceUpdate,
    service: ProductService = Depends(get_product_service),
    admin: dict = Depends(require_admin)
):
    """Update product price. Requires admin role."""
    return await service.update_price(product_id, price_data.price, admin.get("user_id"))


@router.patch("/{product_id}/availability", response_model=ProductResponse)
async def update_product_availability(
    product_id: int,
    availability_data: AvailabilityUpdate,
    service: ProductService = Depends(get_product_service),
    admin: dict = Depends(require_admin)
):
    """Update product availability status. Requires admin role."""
    return await service.update_availability(
        product_id,
        availability_data.is_available,
        admin.get("user_id")
    )


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
    admin: dict = Depends(require_admin)
):
    """Delete a product from the catalog. Requires admin role."""
    await service.delete_product(product_id, admin.get("user_id"))
    return MessageResponse(message=f"Product {product_id} deleted successfully")


@router.post("/categories", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_category(
    category: str = Query(..., min_length=1),
    service: ProductService = Depends(get_product_service),
    admin: dict = Depends(require_admin)
):
    """Add a new product category. Requires admin role."""
    await service.add_category(category, admin.get("user_id"))
    return MessageResponse(message=f"Category '{category}' added successfully")


@router.post("/units", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_unit(
    unit: str = Query(..., min_length=1),
    service: ProductService = Depends(get_product_service),
    admin: dict = Depends(require_admin)
):
    """Add a new product unit. Requires admin role."""
    await service.add_unit(unit, admin.get("user_id"))
    return MessageResponse(message=f"Unit '{unit}' added successfully")
