# Testing Guide

## Overview

The Catalog Service uses a **domain-based testing structure** with comprehensive test coverage across unit, integration, and E2E tests.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── products/                      # Product domain tests
│   ├── unit/                      # Unit tests
│   │   ├── test_product_service.py
│   │   └── test_product_repository.py
│   ├── integration/               # Integration tests
│   │   └── test_product_endpoints.py
│   └── e2e/                       # End-to-end tests
│       └── test_product_workflows.py
└── __init__.py
```

## Test Types

### Unit Tests
**Purpose:** Test individual components in isolation

**Location:** `tests/products/unit/`

**Examples:**
- Service business logic
- Repository data access
- Validation functions

**Run:**
```bash
pytest tests/products/unit/ -m unit
```

### Integration Tests
**Purpose:** Test component interactions

**Location:** `tests/products/integration/`

**Examples:**
- API endpoints
- Service + Repository
- Database operations

**Run:**
```bash
pytest tests/products/integration/ -m integration
```

### E2E Tests
**Purpose:** Test complete workflows

**Location:** `tests/products/e2e/`

**Examples:**
- Complete CRUD workflows
- Multi-step operations
- User journeys

**Run:**
```bash
pytest tests/products/e2e/ -m e2e
```

## Installation

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

## Running Tests

### All Tests
```bash
pytest
```

### Specific Domain
```bash
pytest tests/products/
```

### Specific Type
```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e          # E2E tests only
```

### With Coverage
```bash
pytest --cov=app --cov-report=html
```

### Verbose Output
```bash
pytest -v
```

### Stop on First Failure
```bash
pytest -x
```

## Test Examples

### Unit Test Example
```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_product_success(product_service, sample_product):
    """Test successful product creation."""
    result = await product_service.create_product(sample_product, "admin123")
    
    assert result.id == 1
    assert result.name == "Test Product"
```

### Integration Test Example
```python
@pytest.mark.integration
def test_get_all_products(client):
    """Test getting all products endpoint."""
    response = client.get("/api/v1/products")
    
    assert response.status_code == 200
    assert "items" in response.json()
```

### E2E Test Example
```python
@pytest.mark.e2e
def test_complete_product_lifecycle(client):
    """Test create, read, update, delete workflow."""
    # Create
    create_response = client.post("/api/v1/products", json=data)
    assert create_response.status_code == 201
    
    # Read
    read_response = client.get(f"/api/v1/products/{product_id}")
    assert read_response.status_code == 200
    
    # Update
    update_response = client.patch(f"/api/v1/products/{product_id}/price")
    assert update_response.status_code == 200
    
    # Delete
    delete_response = client.delete(f"/api/v1/products/{product_id}")
    assert delete_response.status_code == 200
```

## Fixtures

### Available Fixtures

**Database & Cache:**
- `mock_db` - Mock database
- `mock_cache` - Mock cache

**Repositories:**
- `product_repository` - Product repository with mock DB

**Services:**
- `product_service` - Product service with mocked dependencies

**Test Data:**
- `sample_product` - Complete product object
- `sample_product_data` - Product data dict
- `admin_user` - Admin user dict
- `regular_user` - Regular user dict

**Client:**
- `client` - FastAPI test client

### Using Fixtures
```python
def test_example(client, sample_product, admin_user):
    """Test using multiple fixtures."""
    response = client.post("/api/v1/products", json=sample_product)
    assert response.status_code == 201
```

## Mocking

### Mock Database
```python
@pytest.mark.asyncio
async def test_with_mock_db(mock_db):
    mock_db.fetch_one = AsyncMock(return_value={"id": 1})
    result = await repository.get_by_id(1)
    assert result.id == 1
```

### Mock Cache
```python
@pytest.mark.asyncio
async def test_with_mock_cache(mock_cache):
    mock_cache.get = AsyncMock(return_value=None)
    result = await service.get_product_by_id(1)
    mock_cache.get.assert_called_once()
```

### Mock External API
```python
def test_with_mock_auth(client):
    with patch('app.dependencies.get_current_user') as mock_auth:
        mock_auth.return_value = {"user_id": "123", "role": "admin"}
        response = client.post("/api/v1/products", json=data)
        assert response.status_code == 201
```

## Test Coverage

### Generate Coverage Report
```bash
pytest --cov=app --cov-report=html
```

### View Report
```bash
# Open htmlcov/index.html in browser
```

### Coverage Goals
- **Unit Tests:** 80%+ coverage
- **Integration Tests:** Key workflows covered
- **E2E Tests:** Critical user journeys

## Best Practices

### 1. Test Naming
```python
# Good
def test_create_product_success()
def test_create_product_invalid_price()
def test_get_product_not_found()

# Bad
def test1()
def test_product()
```

### 2. Arrange-Act-Assert
```python
def test_example():
    # Arrange
    product = Product(name="Test", price=99.99)
    
    # Act
    result = service.create_product(product)
    
    # Assert
    assert result.id is not None
```

### 3. One Assertion Per Test
```python
# Good
def test_product_name():
    assert product.name == "Test"

def test_product_price():
    assert product.price == 99.99

# Avoid
def test_product():
    assert product.name == "Test"
    assert product.price == 99.99
    assert product.type == "HW"
```

### 4. Use Descriptive Names
```python
# Good
def test_create_product_with_negative_price_raises_exception()

# Bad
def test_price()
```

### 5. Test Edge Cases
```python
def test_create_product_with_zero_price()
def test_create_product_with_negative_price()
def test_create_product_with_very_large_price()
def test_create_product_with_empty_name()
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=app
```

## Troubleshooting

### Issue: Async tests not running
**Solution:** Install pytest-asyncio
```bash
pip install pytest-asyncio
```

### Issue: Import errors
**Solution:** Add project root to PYTHONPATH
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: Fixtures not found
**Solution:** Ensure conftest.py is in tests/ directory

## Adding Tests for New Domains

### 1. Create Domain Test Structure
```bash
mkdir tests/customers
mkdir tests/customers/unit
mkdir tests/customers/integration
mkdir tests/customers/e2e
```

### 2. Add Domain Fixtures
```python
# tests/conftest.py
@pytest.fixture
def sample_customer():
    return Customer(id=1, name="Test Customer")
```

### 3. Write Tests
```python
# tests/customers/unit/test_customer_service.py
@pytest.mark.unit
async def test_create_customer(customer_service):
    ...
```

## Summary

✅ **Domain-based structure** - Tests organized by domain
✅ **Three test levels** - Unit, integration, E2E
✅ **Comprehensive fixtures** - Reusable test data
✅ **Mocking support** - Isolated testing
✅ **Coverage reporting** - Track test coverage
✅ **CI/CD ready** - Easy integration
✅ **Best practices** - Clear guidelines
