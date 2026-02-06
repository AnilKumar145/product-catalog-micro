# Naming Conventions

This document outlines the naming conventions used throughout the Catalog Service codebase.

## General Principles

- Use descriptive, meaningful names
- Avoid abbreviations unless widely understood
- Be consistent across the codebase
- Follow Python PEP 8 style guide

## Python Code

### Files and Modules
- **Format**: `snake_case`
- **Examples**: `product_repository.py`, `jwt_handler.py`, `audit_logger.py`

### Classes
- **Format**: `PascalCase`
- **Examples**: `ProductRepository`, `JWTHandler`, `AuditLogger`

### Functions and Methods
- **Format**: `snake_case`
- **Examples**: `get_all_products()`, `update_price()`, `verify_token()`

### Variables
- **Format**: `snake_case`
- **Examples**: `product_id`, `user_name`, `is_available`

### Constants
- **Format**: `UPPER_SNAKE_CASE`
- **Examples**: `DATABASE_URL`, `JWT_SECRET_KEY`, `MAX_PAGE_SIZE`

### Private Members
- **Format**: Prefix with single underscore `_`
- **Examples**: `_internal_method()`, `_cache`

## Database

### Tables
- **Format**: `snake_case`, plural
- **Examples**: `products`, `categories`, `units`

### Columns
- **Format**: `snake_case`
- **Examples**: `product_id`, `created_at`, `is_available`

### Primary Keys
- **Format**: `id`
- **Type**: Serial/Integer

### Foreign Keys
- **Format**: `{table_name}_id`
- **Examples**: `user_id`, `category_id`

### Timestamps
- **Standard Names**: `created_at`, `updated_at`

## API Endpoints

### URL Paths
- **Format**: `kebab-case`, plural for collections
- **Examples**: `/products`, `/categories`, `/business-units`

### Query Parameters
- **Format**: `snake_case`
- **Examples**: `?product_type=HW`, `?page_size=50`, `?sort_by=price`

### HTTP Methods
- `GET` - Retrieve resources
- `POST` - Create resources
- `PUT` - Replace resources
- `PATCH` - Update resources partially
- `DELETE` - Delete resources

## Schemas (Pydantic Models)

### Request Schemas
- **Format**: `{Entity}{Action}`
- **Examples**: `ProductCreate`, `ProductUpdate`, `PriceUpdate`

### Response Schemas
- **Format**: `{Entity}Response`
- **Examples**: `ProductResponse`, `UserResponse`

### Base Schemas
- **Format**: `{Entity}Base`
- **Examples**: `ProductBase`, `UserBase`

## Repositories

### Class Names
- **Format**: `{Entity}Repository`
- **Examples**: `ProductRepository`, `UserRepository`

### Methods
- `get_all()` - Retrieve all records
- `get_by_id(id)` - Retrieve by ID
- `create(entity)` - Create new record
- `update(id, data)` - Update record
- `delete(id)` - Delete record

## Exceptions

### Class Names
- **Format**: `{Description}Exception`
- **Examples**: `NotFoundException`, `UnauthorizedException`

## Middleware

### File Names
- **Format**: `{purpose}_middleware.py`
- **Examples**: `rate_limiter.py`, `audit_middleware.py`

### Function Names
- **Format**: `{purpose}_middleware`
- **Examples**: `rate_limit_middleware()`, `audit_middleware()`

## Configuration

### Environment Variables
- **Format**: `UPPER_SNAKE_CASE`
- **Examples**: `DATABASE_URL`, `JWT_SECRET_KEY`, `LOG_LEVEL`

### Settings Class Attributes
- **Format**: `UPPER_SNAKE_CASE`
- **Examples**: `APP_NAME`, `DATABASE_POOL_SIZE`

## Logging

### Logger Names
- **Format**: Descriptive lowercase
- **Examples**: `"audit"`, `"error"`, `"app"`

### Log Messages
- Use clear, descriptive messages
- Include relevant context
- Start with action verb for operations

## Comments and Docstrings

### Module Docstrings
```python
"""Brief description of module purpose."""
```

### Class Docstrings
```python
class ProductRepository:
    """Repository for product data access."""
```

### Function Docstrings
```python
def get_all_products(filters: dict) -> List[Product]:
    """
    Get all products with optional filters.
    
    Args:
        filters: Dictionary of filter criteria
        
    Returns:
        List of Product objects
    """
```

## Examples

### Good Names ✅
- `product_repository.py`
- `get_all_products()`
- `ProductResponse`
- `DATABASE_URL`
- `/api/v1/products`

### Bad Names ❌
- `prodRepo.py`
- `getAllProds()`
- `ProdResp`
- `dbUrl`
- `/api/v1/prod`

## Consistency Rules

1. **Be consistent within a file** - Use the same naming pattern
2. **Be consistent across files** - Follow established patterns
3. **Be consistent with framework** - Follow FastAPI/Pydantic conventions
4. **Be consistent with database** - Match database naming in models

## Special Cases

### Acronyms
- In PascalCase: `JWTHandler`, `APIException`
- In snake_case: `jwt_token`, `api_key`

### Boolean Variables
- Prefix with `is_`, `has_`, `can_`
- Examples: `is_available`, `has_permission`, `can_edit`

### Collections
- Use plural names
- Examples: `products`, `users`, `categories`

## Version Control

### Branch Names
- **Format**: `{type}/{description}`
- **Examples**: `feature/add-filtering`, `bugfix/rate-limiter`

### Commit Messages
- Start with verb in present tense
- Be descriptive but concise
- Examples: "Add product filtering", "Fix rate limiter bug"
