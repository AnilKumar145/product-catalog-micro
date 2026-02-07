"""Simple in-memory cache implementation."""

from typing import Optional, Any
from datetime import datetime, timedelta
import json


class InMemoryCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self):
        self._cache: dict[str, tuple[Any, datetime]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, expiry = self._cache[key]
            if datetime.now() < expiry:
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL in seconds (default 5 minutes)."""
        expiry = datetime.now() + timedelta(seconds=ttl)
        self._cache[key] = (value, expiry)
    
    def delete(self, key: str):
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        keys_to_delete = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self._cache[key]
    
    def clear(self):
        """Clear entire cache."""
        self._cache.clear()


cache = InMemoryCache()


def get_cache() -> InMemoryCache:
    """Dependency injection for cache."""
    return cache
