"""Service layer dependency injection."""

from fastapi import Depends
from app.services.product_service import ProductService
from app.repositories.product_repository import ProductRepository
from app.infrastructure.cache.redis_cache import RedisCache
from app.dependencies import get_product_repository, get_cache_dependency


async def get_product_service(
    repository: ProductRepository = Depends(get_product_repository),
    cache: RedisCache = Depends(get_cache_dependency)
) -> ProductService:
    """Dependency injection for product service."""
    return ProductService(repository, cache)
