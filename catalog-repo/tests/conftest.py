"""Pytest fixtures for testing."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.models.products import Product
from app.repositories.products import ProductRepository
from app.services.products import ProductService
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.database.connection import Database


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database."""
    db = Mock(spec=Database)
    db.fetch_all = AsyncMock()
    db.fetch_one = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def mock_cache():
    """Mock cache."""
    cache = Mock(spec=RedisCache)
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    cache.clear_pattern = AsyncMock()
    return cache


@pytest.fixture
def product_repository(mock_db):
    """Product repository with mock database."""
    return ProductRepository(mock_db)


@pytest.fixture
def product_service(product_repository, mock_cache):
    """Product service with mocked dependencies."""
    return ProductService(product_repository, mock_cache)


@pytest.fixture
def sample_product():
    """Sample product for testing."""
    return Product(
        id=1,
        name="Test Product",
        description="Test Description",
        category="Hardware",
        unit="Unit",
        business_unit="IT",
        location="US",
        price=99.99,
        product_type="HW",
        is_available=True
    )


@pytest.fixture
def sample_product_data():
    """Sample product data without ID."""
    return {
        "name": "Test Product",
        "description": "Test Description",
        "category": "Hardware",
        "unit": "Unit",
        "business_unit": "IT",
        "location": "US",
        "price": 99.99,
        "product_type": "HW"
    }


@pytest.fixture
def admin_user():
    """Mock admin user."""
    return {
        "user_id": "admin123",
        "username": "admin",
        "role": "admin"
    }


@pytest.fixture
def regular_user():
    """Mock regular user."""
    return {
        "user_id": "user123",
        "username": "user",
        "role": "user"
    }
