# Catalog Service - Enterprise Microservice Template

Enterprise-grade microservice template for BT simulation application. Use this as a blueprint for building additional microservices.

## Quick Start

```bash
# 1. Setup
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Update .env with your credentials

# 3. Run
uvicorn app.main:app --reload --port 8000
```

## Architecture

### Hybrid Domain-Driven Structure
```
app/
├── api/v1/{domain}/          # API endpoints by domain
├── models/{domain}/          # Data models by domain
├── schemas/{domain}/         # Pydantic schemas by domain
├── repositories/{domain}/    # Data access by domain
├── services/{domain}/        # Business logic by domain
├── exceptions/{domain}/      # Domain exceptions
├── infrastructure/           # Shared infrastructure
│   ├── database/            # Connection pooling
│   ├── cache/               # Redis caching
│   ├── messaging/           # RabbitMQ
│   ├── logging/             # Audit & error logs
│   └── security/            # Auth & encryption
├── config/                  # Settings & configuration
├── middleware/              # Rate limiting, audit, errors
├── utils/                   # HTTP client, helpers
└── dependencies.py          # FastAPI dependencies
```

### Layers
1. **API Layer**: HTTP endpoints, request/response handling
2. **Service Layer**: Business logic, validation, caching
3. **Repository Layer**: Database operations
4. **Infrastructure Layer**: External dependencies (DB, cache, messaging)

## Core Features

### Authentication & Authorization
- External auth service integration with retry logic
- JWT token validation
- RBAC: `admin` (full access), `user` (read-only)
- Dependencies: `require_admin()`, `require_user()`

### Database
- PostgreSQL with asyncpg
- Connection pooling (size: 20, min: 10)
- Graceful connection handling with logging

### Caching
- Redis Cloud for distributed caching
- 5-minute TTL, automatic invalidation
- Graceful fallback when unavailable

### Messaging
- RabbitMQ for inter-service communication
- Priority queues (low/medium/high/critical)
- Simple API: `send_to_microservice()`
- Graceful fallback when unavailable

### Resilience
- Timeout & retry for external APIs (5s, 3 retries)
- Exponential backoff with logging
- Graceful degradation for optional services

### Security
- Rate limiting (60 req/min, configurable)
- CORS whitelist
- Environment-based secrets
- Audit logging for all writes

### Monitoring
- Health endpoint: `GET /health`
- Shows status of DB, Redis, RabbitMQ
- Audit logs: `logs/audit.log`
- Error logs: `logs/error.log`

## API Endpoints

### Health
- `GET /` - Service info
- `GET /health` - Infrastructure status

### Products (Example Domain)
- `GET /api/v1/products` - List with filters/pagination
- `GET /api/v1/products/{id}` - Get by ID
- `POST /api/v1/products` - Create (admin)
- `PATCH /api/v1/products/{id}/price` - Update price (admin)
- `PATCH /api/v1/products/{id}/availability` - Update availability (admin)

## Environment Variables

```bash
# Application
APP_NAME=Catalog Service
APP_VERSION=1.0.0

# Database (Required)
DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_POOL_SIZE=20

# Auth (Required)
JWT_SECRET_KEY=your-secret-key
AUTH_SERVICE_URL=http://localhost:8001/api/v1/auth

# External APIs
EXTERNAL_API_TIMEOUT=5
EXTERNAL_API_MAX_RETRIES=3

# Redis (Optional - graceful fallback)
REDIS_URL=redis://default:pass@host:port

# RabbitMQ (Optional - graceful fallback)
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Security
RATE_LIMIT_PER_MINUTE=60
CORS_ORIGINS=["http://localhost:3000"]

# Logging
LOG_LEVEL=INFO
AUDIT_LOG_FILE=logs/audit.log
ERROR_LOG_FILE=logs/error.log
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test types
pytest tests/products/unit/
pytest tests/products/integration/
pytest tests/products/e2e/
```

### Test Structure
```
tests/
├── {domain}/
│   ├── unit/              # Service & repository tests
│   ├── integration/       # API endpoint tests
│   └── e2e/              # Full workflow tests
└── conftest.py           # Shared fixtures
```

## Creating a New Microservice

### 1. Copy Template
```bash
cp -r catalog-service new-service
cd new-service
```

### 2. Update Configuration
- `.env`: Change `APP_NAME`, `DATABASE_URL`, port
- `app/__init__.py`: Update name, version, description
- `requirements.txt`: Add/remove dependencies as needed

### 3. Add Your Domain
```bash
# Create domain structure
mkdir -p app/api/v1/orders
mkdir -p app/models/orders
mkdir -p app/schemas/orders
mkdir -p app/repositories/orders
mkdir -p app/services/orders
mkdir -p app/exceptions/orders
mkdir -p tests/orders/{unit,integration,e2e}
```

### 4. Implement Layers
1. **Model**: Define data structure in `models/orders/`
2. **Schema**: Create Pydantic schemas in `schemas/orders/`
3. **Repository**: Implement data access in `repositories/orders/`
4. **Service**: Add business logic in `services/orders/`
5. **API**: Create endpoints in `api/v1/orders/`
6. **Tests**: Write tests in `tests/orders/`

### 5. Register Routes
```python
# app/api/v1/router.py
from app.api.v1.orders import order_endpoints

router.include_router(
    order_endpoints.router,
    prefix="/v1/orders",
    tags=["Orders"]
)
```

## Best Practices

### Code Quality
- Type hints everywhere
- Docstrings for all public functions
- Pydantic for validation
- Async/await for I/O operations

### Security
- Never commit `.env` (protected by .gitignore)
- Use `.env.example` for templates
- Rotate secrets regularly
- Enable SSL/TLS in production

### Performance
- Use connection pooling
- Cache frequently accessed data
- Implement pagination
- Add database indexes

### Monitoring
- Monitor `/health` endpoint
- Set up log aggregation
- Track error rates
- Monitor response times

## Documentation

- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation guide
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Developer cheat sheet
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture guide
- **[SECURITY.md](SECURITY.md)** - Security best practices
- **[docs/](docs/)** - Additional guides (API, Testing, Messaging, Naming)

## Tech Stack

- **FastAPI** - Web framework
- **PostgreSQL** - Database
- **asyncpg** - Async database driver
- **Redis** - Distributed cache
- **RabbitMQ** - Message broker
- **Pydantic** - Data validation
- **pytest** - Testing framework

## API Documentation

Interactive docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Support

For issues or questions, refer to:
- Architecture documentation in `ARCHITECTURE.md`
- Security guidelines in `SECURITY.md`
- Code examples in existing domains (products)
