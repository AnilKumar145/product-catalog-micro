"""Database connection management with asyncpg."""

import asyncpg
import logging
from typing import Optional
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class Database:
    """Database connection pool manager."""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool."""
        settings = get_settings()
        try:
            self.pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=10,
                max_size=settings.DATABASE_POOL_SIZE,
                max_inactive_connection_lifetime=300
            )
            logger.info("Database connected successfully")
        except Exception as e:
            logger.warning(f"Database connection failed: {e}. Service will run with in-memory fallback.")
            self.pool = None
    
    async def disconnect(self):
        """Close database connection pool."""
        try:
            if self.pool:
                await self.pool.close()
                logger.info("Database disconnected successfully")
        except Exception as e:
            logger.warning(f"Error disconnecting from database: {e}")
    
    async def fetch_all(self, query: str, *args):
        """Execute query and fetch all results."""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetch_one(self, query: str, *args):
        """Execute query and fetch one result."""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def execute(self, query: str, *args):
        """Execute query without returning results."""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)


db = Database()


async def get_db() -> Database:
    """Dependency injection for database."""
    return db
