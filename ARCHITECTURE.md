# Architecture Guide

## Overview

This microservice follows a hybrid domain-driven architecture with clear separation of concerns across four main layers.

## Folder Structure

```
catalog-service/
├── app/
│   ├── api/v1/{domain}/          # API endpoints organized by domain
│   ├── models/{domain}/          # Data models per domain
│   ├── schemas/{domain}/         # Request/response schemas per domain
│   ├── repositories/{domain}/    # Data access layer per domain
│   ├── services/{domain}/        # Business logic per domain
│   ├── exceptions/{domain}/      # Domain-specific exceptions
│   ├── infrastructure/           # Shared infrastructure components
│   │   ├── database/            # Connection pooling, DB utilities
│   │   ├── cache/               # Redis caching
│   │   ├── messaging/           # RabbitMQ message broker
│   │   ├── logging/             # Audit & error logging
│   │   └── security/            # Authentication, encryption
│   ├── config/                  # Application configuration
│   │   ├── settings.py          # Environment-based settings
│   │   ├── cors.py              # CORS configuration
│   │   └── logging.py           # Logging setup
│   ├── middleware/              # HTTP middleware
│   │   ├── rate_limiter.py      # Rate limiting
│   │   ├── audit_middleware.py  # Request auditing
│   │   └── error_handler.py     # Global error handling
│   ├── utils/                   # Shared utilities
│   │   └── http_retry_client.py # HTTP client with retry logic
│   ├── dependencies.py          # FastAPI dependency injection
│   └── main.py                  # Application entry point
├── tests/{domain}/              # Tests organized by domain
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
├── docs/                        # Additional documentation
├── logs/                        # Log files
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
└── README.md                    # Project overview
```

## Layer Responsibilities

### 1. API Layer (`api/v1/{domain}/`)
**Purpose**: Handle HTTP requests and responses

**Responsibilities**:
- Route definitions
- Request validation (via Pydantic)
- Response formatting
- HTTP status codes
- Authentication/authorization checks

**Example**:
```python
@router.get("/products/{id}")
async def get_product(
    id: int,
    service: ProductService = Depends(get_product_service),
    user: dict = Depends(require_user)
):
    return await service.get_product_by_id(id)
```

### 2. Service Layer (`services/{domain}/`)
**Purpose**: Business logic and orchestration

**Responsibilities**:
- Business rules and validation
- Caching logic
- Audit logging
- Orchestrating multiple repositories
- Data transformation

**Example**:
```python
async def update_price(self, product_id: int, new_price: float, user_id: str):
    if new_price <= 0:
        raise InvalidProductPriceException(new_price)
    
    current = await self.repository.get_by_id(product_id)
    
    # Business rule: Alert on >20% price change
    if abs((new_price - current.price) / current.price) > 0.2:
        audit_logger.log("SIGNIFICANT_PRICE_CHANGE", ...)
    
    updated = await self.repository.update_price(product_id, new_price)
    await self.cache.delete(f"product:{product_id}")
    return updated
```

### 3. Repository Layer (`repositories/{domain}/`)
**Purpose**: Data access abstraction

**Responsibilities**:
- Database queries
- CRUD operations
- Query building
- Data mapping (DB ↔ Models)

**Example**:
```python
async def get_by_id(self, product_id: int) -> Product:
    query = "SELECT * FROM products WHERE id = $1"
    row = await self.db.fetch_one(query, product_id)
    if not row:
        raise ProductNotFoundException(product_id)
    return Product(**dict(row))
```

### 4. Infrastructure Layer (`infrastructure/`)
**Purpose**: External service integration

**Components**:
- **Database**: Connection pooling, query execution
- **Cache**: Redis operations with TTL
- **Messaging**: RabbitMQ message broker
- **Logging**: Audit and error logging
- **Security**: JWT validation, encryption

## Request Flow

```
1. HTTP Request
   ↓
2. Middleware (rate limit, audit, error handling)
   ↓
3. API Layer (routing, validation, auth)
   ↓
4. Service Layer (business logic, caching)
   ↓
5. Repository Layer (database operations)
   ↓
6. Infrastructure (DB, cache, messaging)
   ↓
7. Response (formatted, logged)
```

## Domain Organization

Each domain (e.g., products, orders, users) has its own:
- API endpoints
- Data models
- Schemas
- Repository
- Service
- Exceptions
- Tests

**Benefits**:
- Clear boundaries
- Easy to locate code
- Scalable for multiple domains
- Independent testing

## Shared Infrastructure

Infrastructure components are shared across all domains:
- Database connection pool
- Redis cache
- RabbitMQ broker
- Logging utilities
- Security functions

**Benefits**:
- Single source of truth
- Consistent behavior
- Easy to upgrade
- Reduced duplication

## Dependency Injection

FastAPI's DI system provides:
- Loose coupling
- Easy testing (mock dependencies)
- Clear dependencies

**Example**:
```python
# dependencies.py
async def get_product_service(
    repository: ProductRepository = Depends(get_product_repository),
    cache: RedisCache = Depends(get_cache)
) -> ProductService:
    return ProductService(repository, cache)

# endpoint.py
async def create_product(
    product: ProductCreate,
    service: ProductService = Depends(get_product_service),
    user: dict = Depends(require_admin)
):
    return await service.create_product(product, user["id"])
```

## Configuration Management

### Environment-Based
- All config in `.env` file
- Pydantic Settings for validation
- Type-safe access
- Cached for performance

### Settings Structure
```python
class Settings(BaseSettings):
    APP_NAME: str
    DATABASE_URL: str
    REDIS_URL: str
    # ... more settings
    
    class Config:
        env_file = ".env"
```

## Error Handling

### Three Levels
1. **Domain Exceptions**: Business logic errors (404, 400)
2. **Infrastructure Exceptions**: External service failures (503)
3. **Unhandled Exceptions**: Unexpected errors (500)

### Global Handler
Middleware catches all exceptions and:
- Logs to error.log
- Returns appropriate status code
- Hides internal details from clients

## Caching Strategy

### Read-Through Cache
1. Check cache first
2. If miss, query database
3. Store in cache with TTL
4. Return result

### Write-Through Cache
1. Update database
2. Invalidate cache
3. Next read will refresh cache

### Cache Keys
- Structured: `resource:id` or `resource:filters`
- Pattern-based clearing: `products:*`

## Messaging Pattern

### Async Communication
- Send messages to other services
- Priority-based queues
- Fire-and-forget pattern

### Usage
```python
await send_to_microservice(
    to_service="http://localhost:8002/api/v1/orders",
    from_service="catalog-service",
    method="POST",
    message={"product_id": 123, "action": "price_updated"},
    urgency="high"
)
```

## Testing Strategy

### Unit Tests
- Test individual functions
- Mock external dependencies
- Fast execution

### Integration Tests
- Test API endpoints
- Use test database
- Verify layer integration

### E2E Tests
- Test complete workflows
- Simulate real user scenarios
- Verify business requirements

## Scalability Considerations

### Horizontal Scaling
- Stateless design
- Distributed cache (Redis)
- Connection pooling
- Load balancer ready

### Performance
- Async I/O throughout
- Connection reuse
- Efficient queries
- Caching strategy

### Monitoring
- Health checks
- Structured logging
- Audit trail
- Error tracking

## Adding a New Domain

1. Create folder structure:
   ```bash
   mkdir -p app/{api/v1,models,schemas,repositories,services,exceptions}/orders
   mkdir -p tests/orders/{unit,integration,e2e}
   ```

2. Implement layers (bottom-up):
   - Model → Schema → Repository → Service → API

3. Register routes in `app/api/v1/router.py`

4. Write tests for each layer

5. Update documentation

## Best Practices

- **Single Responsibility**: Each layer has one job
- **Dependency Inversion**: Depend on abstractions, not implementations
- **Open/Closed**: Open for extension, closed for modification
- **DRY**: Don't repeat yourself (use shared infrastructure)
- **Type Safety**: Use type hints everywhere
- **Documentation**: Docstrings for all public functions
