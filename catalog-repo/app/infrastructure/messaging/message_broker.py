"""RabbitMQ message broker for inter-service communication."""

import json
import logging
import aio_pika
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class UrgencyLevel(str, Enum):
    """Message urgency levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MessageBroker:
    """RabbitMQ message broker for async messaging between microservices."""
    
    def __init__(self):
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.settings = get_settings()
    
    async def connect(self):
        """Connect to RabbitMQ."""
        try:
            self.connection = await aio_pika.connect_robust(self.settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)
            logger.info("RabbitMQ connected successfully")
        except Exception as e:
            logger.warning(f"RabbitMQ connection failed: {e}. Service will run without messaging.")
            self.connection = None
            self.channel = None
    
    async def disconnect(self):
        """Disconnect from RabbitMQ."""
        try:
            if self.channel:
                await self.channel.close()
            if self.connection:
                await self.connection.close()
        except Exception as e:
            logger.warning(f"Error disconnecting from RabbitMQ: {e}")
    
    async def send_message(
        self,
        to_service: str,
        from_service: str,
        method: str,
        message: Dict[str, Any],
        urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    ) -> bool:
        """
        Send async message to another microservice.
        
        Args:
            to_service: Target service URL or queue name
            from_service: Source service identifier
            method: HTTP method or action type (GET, POST, etc.)
            message: Message payload
            urgency: Message urgency level
        
        Returns:
            bool: True if message sent successfully
        """
        if not self.channel:
            await self.connect()
        
        if not self.channel:
            logger.warning("RabbitMQ not available. Message not sent.")
            return False
        
        # Create queue name from service URL
        queue_name = self._get_queue_name(to_service)
        
        # Declare queue
        queue = await self.channel.declare_queue(
            queue_name,
            durable=True,
            arguments={"x-max-priority": 10}
        )
        
        # Prepare message
        message_body = {
            "from_service": from_service,
            "to_service": to_service,
            "method": method,
            "payload": message,
            "urgency": urgency.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Set priority based on urgency
        priority = self._get_priority(urgency)
        
        # Publish message
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message_body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                priority=priority,
                content_type="application/json"
            ),
            routing_key=queue_name
        )
        
        return True
    
    async def consume_messages(
        self,
        service_name: str,
        callback
    ):
        """
        Consume messages for this service.
        
        Args:
            service_name: This service's identifier
            callback: Async function to handle messages
        """
        if not self.channel:
            await self.connect()
        
        if not self.channel:
            logger.warning("RabbitMQ not available. Cannot consume messages.")
            return
        
        queue_name = self._get_queue_name(service_name)
        
        queue = await self.channel.declare_queue(
            queue_name,
            durable=True,
            arguments={"x-max-priority": 10}
        )
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = json.loads(message.body.decode())
                    await callback(body)
    
    def _get_queue_name(self, service_url: str) -> str:
        """Extract queue name from service URL."""
        # Remove protocol and convert to queue name
        queue_name = service_url.replace("http://", "").replace("https://", "")
        queue_name = queue_name.replace("/", "_").replace(":", "_")
        return f"queue_{queue_name}"
    
    def _get_priority(self, urgency: UrgencyLevel) -> int:
        """Get message priority from urgency level."""
        priority_map = {
            UrgencyLevel.LOW: 1,
            UrgencyLevel.MEDIUM: 5,
            UrgencyLevel.HIGH: 8,
            UrgencyLevel.CRITICAL: 10
        }
        return priority_map.get(urgency, 5)


# Global message broker instance
message_broker = MessageBroker()


async def send_to_microservice(
    to_service: str,
    from_service: str,
    method: str,
    message: Dict[str, Any],
    urgency: str = "medium"
) -> bool:
    """
    Simple function to send message to another microservice.
    
    Args:
        to_service: Target service URL (e.g., "http://localhost:8002/api/v1/orders")
        from_service: Source service name (e.g., "catalog-service")
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        message: Message payload as dictionary
        urgency: Urgency level (low, medium, high, critical)
    
    Returns:
        bool: True if sent successfully
    
    Example:
        await send_to_microservice(
            to_service="http://localhost:8002/api/v1/orders",
            from_service="catalog-service",
            method="POST",
            message={"product_id": 123, "action": "price_updated"},
            urgency="high"
        )
    """
    urgency_level = UrgencyLevel(urgency.lower())
    return await message_broker.send_message(
        to_service=to_service,
        from_service=from_service,
        method=method,
        message=message,
        urgency=urgency_level
    )
