"""Product service - Business logic layer."""

from typing import List, Optional, Tuple
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.logging.audit_logger import audit_logger


class ProductService:
    """Service layer for product business logic."""
    
    def __init__(self, repository: ProductRepository, cache: RedisCache):
        self.repository = repository
        self.cache = cache
    
    async def get_all_products(
        self,
        product_type: Optional[str] = None,
        business_unit: Optional[str] = None,
        location: Optional[str] = None,
        category: Optional[str] = None,
        sort_by: str = "id",
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Product], int]:
        """Get all products with caching."""
        cache_key = f"products:{product_type}:{business_unit}:{location}:{category}:{sort_by}:{page}:{page_size}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            return cached['items'], cached['total']
        
        products, total = await self.repository.get_all(
            product_type=product_type,
            business_unit=business_unit,
            location=location,
            category=category,
            sort_by=sort_by,
            page=page,
            page_size=page_size
        )
        
        await self.cache.set(cache_key, {'items': products, 'total': total}, ttl=300)
        return products, total
    
    async def get_product_by_id(self, product_id: int) -> Product:
        """Get product by ID with caching."""
        cache_key = f"product:{product_id}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            return Product(**cached)
        
        product = await self.repository.get_by_id(product_id)
        await self.cache.set(cache_key, product.model_dump(), ttl=300)
        return product
    
    async def create_product(self, product: Product, user_id: str) -> Product:
        """Create product with business validation and cache invalidation."""
        # Business validation
        if product.price <= 0:
            raise ValueError("Price must be greater than 0")
        
        if product.product_type not in ["HW", "SW"]:
            raise ValueError("Product type must be HW or SW")
        
        # Create product
        created_product = await self.repository.create(product)
        
        # Invalidate cache
        await self.cache.clear_pattern("products:")
        
        # Audit log
        audit_logger.log(
            user_id=user_id,
            action="CREATE_PRODUCT",
            resource=f"products/{created_product.id}",
            details={"product_name": created_product.name}
        )
        
        return created_product
    
    async def update_price(self, product_id: int, new_price: float, user_id: str) -> Product:
        """Update product price with business rules."""
        # Business validation
        if new_price <= 0:
            raise ValueError("Price must be greater than 0")
        
        # Get current product
        current_product = await self.repository.get_by_id(product_id)
        
        # Business rule: Log significant price changes
        price_change_percent = abs((new_price - current_product.price) / current_product.price * 100)
        if price_change_percent > 20:
            audit_logger.log(
                user_id=user_id,
                action="SIGNIFICANT_PRICE_CHANGE",
                resource=f"products/{product_id}",
                details={
                    "old_price": current_product.price,
                    "new_price": new_price,
                    "change_percent": price_change_percent
                }
            )
        
        # Update price
        updated_product = await self.repository.update_price(product_id, new_price)
        
        # Invalidate cache
        await self.cache.delete(f"product:{product_id}")
        await self.cache.clear_pattern("products:")
        
        return updated_product
    
    async def update_availability(self, product_id: int, is_available: bool, user_id: str) -> Product:
        """Update product availability."""
        updated_product = await self.repository.update_availability(product_id, is_available)
        
        # Invalidate cache
        await self.cache.delete(f"product:{product_id}")
        await self.cache.clear_pattern("products:")
        
        # Audit log
        audit_logger.log(
            user_id=user_id,
            action="UPDATE_AVAILABILITY",
            resource=f"products/{product_id}",
            details={"is_available": is_available}
        )
        
        return updated_product
    
    async def delete_product(self, product_id: int, user_id: str) -> None:
        """Delete product with business validation."""
        # Business rule: Check if product can be deleted
        product = await self.repository.get_by_id(product_id)
        
        # Could add checks like:
        # - Is product in active orders?
        # - Is product referenced elsewhere?
        
        # Delete product
        await self.repository.delete(product_id)
        
        # Invalidate cache
        await self.cache.delete(f"product:{product_id}")
        await self.cache.clear_pattern("products:")
        
        # Audit log
        audit_logger.log(
            user_id=user_id,
            action="DELETE_PRODUCT",
            resource=f"products/{product_id}",
            details={"product_name": product.name}
        )
    
    async def add_category(self, category: str, user_id: str) -> dict:
        """Add new category with validation."""
        if not category or len(category) < 2:
            raise ValueError("Category name must be at least 2 characters")
        
        result = await self.repository.add_category(category)
        
        audit_logger.log(
            user_id=user_id,
            action="ADD_CATEGORY",
            resource="categories",
            details={"category": category}
        )
        
        return result
    
    async def add_unit(self, unit: str, user_id: str) -> dict:
        """Add new unit with validation."""
        if not unit or len(unit) < 1:
            raise ValueError("Unit name must be at least 1 character")
        
        result = await self.repository.add_unit(unit)
        
        audit_logger.log(
            user_id=user_id,
            action="ADD_UNIT",
            resource="units",
            details={"unit": unit}
        )
        
        return result
