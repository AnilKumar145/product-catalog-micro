# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except health checks) require JWT authentication.

**Header:**
```
Authorization: Bearer <jwt_token>
```

## Endpoints

### Health Check

#### GET /
Root endpoint - service information

**Response:**
```json
{
  "service": "Catalog Service",
  "version": "1.0.0",
  "status": "healthy"
}
```

#### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Products

#### GET /api/v1/products
Get all products with filters and pagination

**Authentication:** Required

**Query Parameters:**
- `product_type` (optional): Filter by HW or SW
- `business_unit` (optional): Filter by business unit
- `location` (optional): Filter by location
- `category` (optional): Filter by category
- `sort_by` (optional): Sort field (default: id)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 50, max: 100)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/products?product_type=HW&location=US&page=1&page_size=20" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Dell PowerEdge R740",
      "description": "Enterprise server",
      "category": "Servers",
      "unit": "Server",
      "business_unit": "Infrastructure",
      "location": "US",
      "price": 5999.99,
      "product_type": "HW",
      "is_available": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

#### GET /api/v1/products/{product_id}
Get product by ID

**Authentication:** Required

**Path Parameters:**
- `product_id`: Product ID

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/products/1" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "id": 1,
  "name": "Dell PowerEdge R740",
  "description": "Enterprise server",
  "category": "Servers",
  "unit": "Server",
  "business_unit": "Infrastructure",
  "location": "US",
  "price": 5999.99,
  "product_type": "HW",
  "is_available": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

#### POST /api/v1/products
Add a new product

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "name": "Dell PowerEdge R740",
  "description": "Enterprise server with dual processors",
  "category": "Servers",
  "unit": "Server",
  "business_unit": "Infrastructure",
  "location": "US",
  "price": 5999.99,
  "product_type": "HW"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dell PowerEdge R740",
    "description": "Enterprise server",
    "category": "Servers",
    "unit": "Server",
    "business_unit": "Infrastructure",
    "location": "US",
    "price": 5999.99,
    "product_type": "HW"
  }'
```

**Response:** (201 Created)
```json
{
  "id": 1,
  "name": "Dell PowerEdge R740",
  "description": "Enterprise server",
  "category": "Servers",
  "unit": "Server",
  "business_unit": "Infrastructure",
  "location": "US",
  "price": 5999.99,
  "product_type": "HW",
  "is_available": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

#### PATCH /api/v1/products/{product_id}/price
Update product price

**Authentication:** Required (Admin only)

**Path Parameters:**
- `product_id`: Product ID

**Request Body:**
```json
{
  "price": 6499.99
}
```

**Example Request:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/products/1/price" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"price": 6499.99}'
```

**Response:**
```json
{
  "id": 1,
  "name": "Dell PowerEdge R740",
  "price": 6499.99,
  ...
}
```

---

#### PATCH /api/v1/products/{product_id}/availability
Update product availability

**Authentication:** Required (Admin only)

**Path Parameters:**
- `product_id`: Product ID

**Request Body:**
```json
{
  "is_available": false
}
```

**Example Request:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/products/1/availability" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"is_available": false}'
```

**Response:**
```json
{
  "id": 1,
  "name": "Dell PowerEdge R740",
  "is_available": false,
  ...
}
```

---

### Categories

#### POST /api/v1/products/categories
Add a new category

**Authentication:** Required (Admin only)

**Query Parameters:**
- `category`: Category name

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/products/categories?category=Cloud%20Services" \
  -H "Authorization: Bearer <admin_token>"
```

**Response:** (201 Created)
```json
{
  "message": "Category 'Cloud Services' added successfully"
}
```

---

### Units

#### POST /api/v1/products/units
Add a new unit

**Authentication:** Required (Admin only)

**Query Parameters:**
- `unit`: Unit name

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/products/units?unit=Subscription" \
  -H "Authorization: Bearer <admin_token>"
```

**Response:** (201 Created)
```json
{
  "message": "Unit 'Subscription' added successfully"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Missing or invalid authorization header"
}
```

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found
```json
{
  "detail": "Product not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

- Default: 60 requests per minute per IP
- Exceeding limit returns 429 status code

---

## Pagination

All list endpoints support pagination:
- `page`: Page number (starts at 1)
- `page_size`: Items per page (max 100)

Response includes:
- `items`: Array of results
- `total`: Total number of items
- `page`: Current page
- `page_size`: Items per page
- `total_pages`: Total number of pages

---

## Filtering

Products can be filtered by:
- `product_type`: HW or SW
- `business_unit`: Business unit name
- `location`: Location code
- `category`: Category name

Multiple filters can be combined.

---

## Sorting

Use `sort_by` parameter with field name:
- `id` (default)
- `name`
- `price`
- `created_at`

---

## Interactive Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
