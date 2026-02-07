# Async Messaging Between Microservices

## Overview

The Catalog Service implements **RabbitMQ-based async messaging** for inter-service communication with priority queues and urgency levels.

## Architecture

```
Catalog Service
    ↓ (send message)
RabbitMQ Broker
    ↓ (route to queue)
Target Service
    ↓ (consume message)
Process & Respond
```

## Configuration

### Environment Variable

```env
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

**Production Example:**
```env
RABBITMQ_URL=amqp://user:password@rabbitmq.example.com:5672/vhost
```

## Installation

```bash
pip install aio-pika==9.3.1
```

## Usage

### Simple Message Sending

```python
from app.infrastructure.messaging import send_to_microservice

# Send message to another service
await send_to_microservice(
    to_service="http://localhost:8002/api/v1/orders",
    from_service="catalog-service",
    method="POST",
    message={"product_id": 123, "action": "price_updated"},
    urgency="high"
)
```

### Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `to_service` | str | Target service URL | `"http://localhost:8002/api/v1/orders"` |
| `from_service` | str | Source service name | `"catalog-service"` |
| `method` | str | HTTP method/action | `"POST"`, `"GET"`, `"DELETE"` |
| `message` | dict | Message payload | `{"product_id": 123}` |
| `urgency` | str | Priority level | `"low"`, `"medium"`, `"high"`, `"critical"` |

## Urgency Levels

| Level | Priority | Use Case |
|-------|----------|----------|
| `low` | 1 | Background tasks, analytics |
| `medium` | 5 | Standard notifications |
| `high` | 8 | Important updates, price changes |
| `critical` | 10 | System alerts, deletions |

## Examples

### Example 1: Notify Price Change

```python
from app.infrastructure.messaging import send_to_microservice

async def notify_price_change(product_id: int, new_price: float):
    """Notify order service about price change."""
    await send_to_microservice(
        to_service="http://localhost:8002/api/v1/orders",
        from_service="catalog-service",
        method="POST",
        message={
            "event": "product.price_changed",
            "product_id": product_id,
            "new_price": new_price,
            "timestamp": datetime.utcnow().isoformat()
        },
        urgency="high"
    )
```

### Example 2: Product Created Event

```python
async def notify_product_created(product_id: int, product_data: dict):
    """Notify inventory service about new product."""
    await send_to_microservice(
        to_service="http://localhost:8003/api/v1/inventory",
        from_service="catalog-service",
        method="POST",
        message={
            "event": "product.created",
            "product_id": product_id,
            "product_data": product_data
        },
        urgency="medium"
    )
```

### Example 3: Request Data

```python
async def request_supplier_info(product_id: int):
    """Request supplier information."""
    await send_to_microservice(
        to_service="http://localhost:8004/api/v1/suppliers",
        from_service="catalog-service",
        method="GET",
        message={
            "action": "get_supplier_info",
            "product_id": product_id
        },
        urgency="low"
    )
```

### Example 4: Critical Notification

```python
async def notify_product_deleted(product_id: int):
    """Notify all services about product deletion."""
    services = [
        "http://localhost:8002/api/v1/orders",
        "http://localhost:8003/api/v1/inventory"
    ]
    
    for service in services:
        await send_to_microservice(
            to_service=service,
            from_service="catalog-service",
            method="DELETE",
            message={
                "event": "product.deleted",
                "product_id": product_id
            },
            urgency="critical"
        )
```

## Integration in Service Layer

```python
# app/services/products/product_service.py
from app.infrastructure.messaging import send_to_microservice

class ProductService:
    async def update_price(self, product_id: int, new_price: float, user_id: str):
        """Update price and notify other services."""
        # Update in database
        updated_product = await self.repository.update_price(product_id, new_price)
        
        # Notify other services
        await send_to_microservice(
            to_service="http://localhost:8002/api/v1/orders",
            from_service="catalog-service",
            method="POST",
            message={
                "event": "product.price_changed",
                "product_id": product_id,
                "new_price": new_price
            },
            urgency="high"
        )
        
        return updated_product
```

## Message Format

### Sent Message Structure

```json
{
  "from_service": "catalog-service",
  "to_service": "http://localhost:8002/api/v1/orders",
  "method": "POST",
  "payload": {
    "event": "product.price_changed",
    "product_id": 123,
    "new_price": 99.99
  },
  "urgency": "high",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Consuming Messages

### Setup Message Consumer

```python
from app.infrastructure.messaging import message_broker

async def handle_message(message: dict):
    """Handle incoming message."""
    print(f"Received from: {message['from_service']}")
    print(f"Method: {message['method']}")
    print(f"Payload: {message['payload']}")
    
    # Process message
    if message['payload'].get('event') == 'order.created':
        product_id = message['payload']['product_id']
        # Update inventory, etc.

# Start consuming
await message_broker.consume_messages(
    service_name="catalog-service",
    callback=handle_message
)
```

## Queue Naming

Queues are automatically named based on service URL:

| Service URL | Queue Name |
|-------------|------------|
| `http://localhost:8002/api/v1/orders` | `queue_localhost_8002_api_v1_orders` |
| `http://order-service/api/v1` | `queue_order-service_api_v1` |

## Features

### ✅ Priority Queues
Messages are prioritized based on urgency level (1-10)

### ✅ Persistent Messages
Messages survive RabbitMQ restarts

### ✅ Automatic Reconnection
Connection is automatically restored on failure

### ✅ Async/Non-blocking
All operations are async using aio-pika

### ✅ Simple API
One function call to send messages

## RabbitMQ Setup

### Local Development

```bash
# Using Docker
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management

# Access management UI
http://localhost:15672
# Username: guest
# Password: guest
```

### Production

```env
RABBITMQ_URL=amqp://user:password@rabbitmq-prod.example.com:5672/production
```

## Monitoring

### RabbitMQ Management UI

Access at: `http://localhost:15672`

**View:**
- Queue lengths
- Message rates
- Consumer status
- Connection details

### Health Check

```python
@app.get("/health/messaging")
async def check_messaging():
    """Check RabbitMQ connection."""
    try:
        if message_broker.connection and not message_broker.connection.is_closed:
            return {"messaging": "healthy"}
        return {"messaging": "unhealthy"}
    except:
        return {"messaging": "unhealthy"}
```

## Error Handling

```python
try:
    await send_to_microservice(
        to_service="http://localhost:8002/api/v1/orders",
        from_service="catalog-service",
        method="POST",
        message={"data": "test"},
        urgency="medium"
    )
except Exception as e:
    logger.error(f"Failed to send message: {e}")
    # Handle error (retry, alert, etc.)
```

## Best Practices

### 1. Use Appropriate Urgency
```python
# Critical - system alerts
urgency="critical"

# High - important updates
urgency="high"

# Medium - standard notifications
urgency="medium"

# Low - background tasks
urgency="low"
```

### 2. Include Timestamps
```python
message={
    "event": "product.updated",
    "timestamp": datetime.utcnow().isoformat()
}
```

### 3. Use Event Names
```python
message={
    "event": "product.price_changed",  # Clear event name
    "product_id": 123
}
```

### 4. Keep Messages Small
```python
# Good - send ID
message={"product_id": 123}

# Bad - send entire object
message={"product": {...}}  # Large payload
```

### 5. Handle Failures
```python
try:
    await send_to_microservice(...)
except Exception as e:
    # Log error
    # Retry logic
    # Alert monitoring
```

## Testing

### Mock Messaging in Tests

```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_price_update_sends_message():
    with patch('app.infrastructure.messaging.send_to_microservice') as mock_send:
        mock_send.return_value = AsyncMock(return_value=True)
        
        await service.update_price(1, 99.99, "admin")
        
        mock_send.assert_called_once()
```

## Troubleshooting

### Issue: Connection refused
**Solution:** Ensure RabbitMQ is running
```bash
docker ps | grep rabbitmq
```

### Issue: Messages not delivered
**Solution:** Check queue exists in RabbitMQ UI

### Issue: Slow message processing
**Solution:** Increase consumer count or optimize handler

## Summary

✅ **RabbitMQ-based** - Industry standard message broker
✅ **Priority queues** - Urgency-based message handling
✅ **Simple API** - One function to send messages
✅ **Async/Non-blocking** - Full async support
✅ **Persistent** - Messages survive restarts
✅ **Production ready** - Robust error handling
✅ **Easy integration** - Drop-in component
