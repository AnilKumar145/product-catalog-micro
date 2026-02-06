"""Example: Using messaging in product service."""

from app.infrastructure.messaging import send_to_microservice


# Example 1: Notify order service when price changes
async def notify_price_change(product_id: int, old_price: float, new_price: float):
    """Notify order service about price change."""
    await send_to_microservice(
        to_service="http://localhost:8002/api/v1/orders",
        from_service="catalog-service",
        method="POST",
        message={
            "event": "product.price_changed",
            "product_id": product_id,
            "old_price": old_price,
            "new_price": new_price
        },
        urgency="high"
    )


# Example 2: Notify inventory service when product created
async def notify_product_created(product_id: int, product_name: str):
    """Notify inventory service about new product."""
    await send_to_microservice(
        to_service="http://localhost:8003/api/v1/inventory",
        from_service="catalog-service",
        method="POST",
        message={
            "event": "product.created",
            "product_id": product_id,
            "product_name": product_name
        },
        urgency="medium"
    )


# Example 3: Request data from another service
async def request_supplier_info(product_id: int):
    """Request supplier information from supplier service."""
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


# Example 4: Critical notification
async def notify_product_deleted(product_id: int):
    """Notify all services about product deletion."""
    services = [
        "http://localhost:8002/api/v1/orders",
        "http://localhost:8003/api/v1/inventory",
        "http://localhost:8004/api/v1/suppliers"
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
