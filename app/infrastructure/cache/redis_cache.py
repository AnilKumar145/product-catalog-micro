"""Redis cloud cache implementation."""

import json
import logging
from typing import Optional, Any
import redis.asyncio as redis
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache manager for cloud-based caching."""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis cloud."""
        settings = get_settings()
        try:
            self.redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5
            )
            await self.redis.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Service will run without caching.")
            self.redis = None
    
    async def disconnect(self):
        """Disconnect from Redis."""
        try:
            if self.redis:
                await self.redis.close()
        except Exception as e:
            logger.warning(f"Error disconnecting from Redis: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis:
            return None
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (default 5 minutes)."""
        if self.redis:
            try:
                await self.redis.setex(key, ttl, json.dumps(value, default=str))
            except Exception:
                pass
    
    async def delete(self, key: str):
        """Delete key from cache."""
        if self.redis:
            try:
                await self.redis.delete(key)
            except Exception:
                pass
    
    async def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        if self.redis:
            try:
                keys = await self.redis.keys(f"{pattern}*")
                if keys:
                    await self.redis.delete(*keys)
            except Exception:
                pass
    
    async def ping(self) -> bool:
        """Check Redis connection."""
        if self.redis:
            try:
                return await self.redis.ping()
            except Exception:
                return False
        return False


cache = RedisCache()


async def get_cache() -> RedisCache:
    """Dependency injection for cache."""
    return cache
