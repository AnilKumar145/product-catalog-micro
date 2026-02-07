"""FastAPI dependencies for authentication and authorization."""

from fastapi import Depends, Header, HTTPException, status
from typing import Optional
import httpx
from app.config.settings import get_settings
from app.infrastructure.database.connection import get_db, Database
from app.repositories.product_repository import ProductRepository
from app.infrastructure.cache.redis_cache import get_cache, RedisCache
from app.utils.http_retry_client import http_client


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency to get current authenticated user from external auth service with retry logic."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    settings = get_settings()
    
    try:
        response = await http_client.post(
            f"{settings.AUTH_SERVICE_URL}/verify",
            json={"token": token}
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth service returned {response.status_code}"
            )
    
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service timeout"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Authentication service unavailable: {str(e)}"
        )


async def require_role(required_role: str):
    """Factory function to create role-based dependencies."""
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "user")
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role.capitalize()} access required"
            )
        return current_user
    return role_checker


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to require admin role."""
    user_role = current_user.get("role", "user")
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to require user or admin role."""
    user_role = current_user.get("role", "user")
    if user_role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User access required"
        )
    return current_user


async def get_product_repository(db: Database = Depends(get_db)) -> ProductRepository:
    """Dependency injection for product repository."""
    return ProductRepository(db)


async def get_cache_dependency() -> RedisCache:
    """Dependency injection for cache."""
    return get_cache()
