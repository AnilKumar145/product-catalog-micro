"""Main FastAPI application."""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app import __version__, __description__
from app.config.settings import get_settings
from app.config.cors import setup_cors
from app.config.logging import setup_logging
from app.infrastructure.database.connection import db
from app.infrastructure.cache.redis_cache import cache
from app.infrastructure.messaging.message_broker import message_broker
from app.api.v1 import router as v1_router
from app.middleware.rate_limiter import rate_limit_middleware
from app.middleware.audit_middleware import audit_middleware
from app.middleware.error_handler import error_handler_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    setup_logging()
    await db.connect()
    await cache.connect()
    await message_broker.connect()
    yield
    await message_broker.disconnect()
    await cache.disconnect()
    await db.disconnect()


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

setup_cors(app)

app.middleware("http")(error_handler_middleware)
app.middleware("http")(audit_middleware)
app.middleware("http")(rate_limit_middleware)

app.include_router(v1_router.router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    db_status = "healthy" if db.pool else "unavailable"
    cache_status = "healthy" if await cache.ping() else "unavailable"
    rabbitmq_status = "healthy" if message_broker.channel else "unavailable"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "cache": cache_status,
        "messaging": rabbitmq_status
    }
