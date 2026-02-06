# Quick Reference Guide

## Project Structure

```
catalog-service/
├── app/
│   ├── api/v1/{domain}/          # API endpoints
│   ├── models/{domain}/          # Data models
│   ├── schemas/{domain}/         # Pydantic schemas
│   ├── repositories/{domain}/    # Data access
│   ├── services/{domain}/        # Business logic
│   ├── exceptions/{domain}/      # Domain exceptions
│   ├── infrastructure/           # DB, cache, messaging
│   ├── config/                   # Settings
│   ├── middleware/               # Rate limit, audit, errors
│   ├── utils/                    # HTTP client, helpers
│   └── dependencies.py           # DI
├── tests/{domain}/               # Tests by domain
├── docs/                         # Documentation
├── .env                          # Environment variables
└── requirements.txt              # Dependencies
```

## Common Commands

```bash
# Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Run
uvicorn app.main:app --reload --port 8000

# Test
pytest                           # All tests
pytest tests/products/unit/      # Unit tests
pytest --cov=app                 # With coverage

# Dependencies
pip freeze > requirements.txt
pip install safety && safety check
```

## Environment Variables

```env
# Required
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET_KEY=your-secret-key
AUTH_SERVICE_URL=http://localhost:8001/api/v1/auth

# Optional (graceful fallback)
REDIS_URL=redis://default:pass@host:port
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Configuration
RATE_LIMIT_PER_MINUTE=60
CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO
```

## Adding a New Domain

```bash
# 1. Create structure
mkdir -p app/{api/v1,models,schemas,repositories,services,exceptions}/orders
mkdir -p tests/orders/{unit,integration,e2e}

# 2. Implement layers (bottom-up)
# - models/orders/order.py
# - schemas/orders/order_schemas.py
# - repositories/orders/order_repository.py
# - services/orders/order_service.py
# - api/v1/orders/order_endpoints.py

# 3. Register routes in app/api/v1/router.py
```

## Code Templates

### Model
```python
from pydantic import BaseModel
from datetime import datetime

class Order(BaseModel):
    id: int
    product_id: int
    quantity: int
    created_at: datetime
```

### Repository
```python
class OrderRepository:
    def __init__(self, db: Database):
        self.db = db
    
    async def get_by_id(self, order_id: int) -> Order:
        query = "SELECT * FROM orders WHERE id = $1"
        row = await self.db.fetch_one(query, order_id)
        if not row:
            raise OrderNotFoundException(order_id)
        return Order(**dict(row))
```

### Service
```python
class OrderService:
    def __init__(self, repository: OrderRepository, cache: RedisCache):
        self.repository = repository
        self.cache = cache
    
    async def get_order(self, order_id: int) -> Order:
        cache_key = f"order:{order_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return Order(**cached)
        
        order = await self.repository.get_by_id(order_id)
        await self.cache.set(cache_key, order.model_dump())
        return order
```

### API Endpoint
```python
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/orders/{id}")
async def get_order(
    id: int,
    service: OrderService = Depends(get_order_service),
    user: dict = Depends(require_user)
):
    return await service.get_order(id)
```

## Authentication

```python
# In endpoints
from app.dependencies import require_admin, require_user

@router.post("/products")
async def create_product(
    product: ProductCreate,
    user: dict = Depends(require_admin)  # Admin only
):
    pass

@router.get("/products")
async def list_products(
    user: dict = Depends(require_user)  # Any authenticated user
):
    pass
```

## Caching

```python
# Read with cache
cache_key = f"product:{product_id}"
cached = await self.cache.get(cache_key)
if cached:
    return Product(**cached)

result = await self.repository.get_by_id(product_id)
await self.cache.set(cache_key, result.model_dump(), ttl=300)
return result

# Invalidate on write
await self.cache.delete(f"product:{product_id}")
await self.cache.clear_pattern("products:")
```

## Messaging

```python
from app.infrastructure.messaging import send_to_microservice

await send_to_microservice(
    to_service="http://localhost:8002/api/v1/orders",
    from_service="catalog-service",
    method="POST",
    message={"product_id": 123, "action": "price_updated"},
    urgency="high"  # low, medium, high, critical
)
```

## Testing

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_product(product_service, mock_cache):
    mock_cache.get = AsyncMock(return_value=None)
    result = await product_service.get_product_by_id(1)
    assert result.id == 1
```

## Common Patterns

### Error Handling
```python
from app.exceptions.products import ProductNotFoundException

if not product:
    raise ProductNotFoundException(product_id)
```

### Pagination
```python
@router.get("/products")
async def list_products(
    page: int = 1,
    page_size: int = 50
):
    products, total = await service.get_all(page, page_size)
    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size
    }
```

### Audit Logging
```python
from app.infrastructure.logging.audit_logger import audit_logger

audit_logger.log(
    user_id=user["id"],
    action="CREATE_PRODUCT",
    resource=f"products/{product.id}",
    details={"name": product.name}
)
```

## Health Check

```bash
# Check service health
curl http://localhost:8000/health

# Response shows infrastructure status
{
  "status": "healthy",
  "database": "healthy",
  "cache": "healthy",
  "messaging": "healthy"
}
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Database connection failed
- Check DATABASE_URL in .env
- Ensure PostgreSQL is running
- Verify credentials

### Redis/RabbitMQ unavailable
- Service runs with graceful fallback
- Check logs for warnings
- Optional components, not required

### Import errors
- Activate virtual environment
- Install dependencies: `pip install -r requirements.txt`

### Tests failing
- Install test dependencies: `pip install pytest pytest-asyncio`
- Check conftest.py exists in tests/

## Documentation

- `README.md` - Overview & quick start
- `ARCHITECTURE.md` - Detailed architecture
- `SECURITY.md` - Security best practices
- `docs/API_DOCUMENTATION.md` - API reference
- `docs/TESTING.md` - Testing guide
- `docs/MESSAGING.md` - Async messaging
- `docs/NAMING_CONVENTIONS.md` - Code standards

## Support

For detailed information, refer to the documentation files above.
