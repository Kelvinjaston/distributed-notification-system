import aio_pika
import os
import json
import logging
from typing import Optional

# Setup logging
logger = logging.getLogger(__name__)

# Load RabbitMQ URL from environment
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
TEMPLATE_EXCHANGE = "template_events.fanout" # Exchange for cache invalidation

class MessagingService:
    """
    Manages the RabbitMQ connection and message publishing.
    """
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.connection: Optional[aio_pika.RobustConnection] = None

    async def init_rabbitmq_connection(self):
        """
        Initializes the RabbitMQ connection.
        Call this during the FastAPI lifespan startup.
        """
        try:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            logger.info("RabbitMQ connection initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize RabbitMQ connection: {e}")

    async def close_rabbitmq_connection(self):
        """
        Closes the RabbitMQ connection.
        Call this during the FastAPI lifespan shutdown.
        """
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed.")

    async def get_channel(self) -> Optional[aio_pika.Channel]:
        """
        Gets a new channel from the connection.
        """
        if not self.connection:
            logger.error("RabbitMQ connection is not initialized.")
            return None
        return await self.connection.channel()

    async def publish_template_update_message(self, name: str, language: str):
        """
        Publishes a cache invalidation message to the fanout exchange.
        This tells other services to clear their cache for this template.
        """
        channel = await self.get_channel()
        if not channel:
            return

        async with channel:
            try:
                # Declare the fanout exchange, 'durable=True' means it survives broker restarts
                exchange = await channel.declare_exchange(
                    TEMPLATE_EXCHANGE,
                    type=aio_pika.ExchangeType.FANOUT,
                    durable=True
                )
                
                message_body = {
                    "event": "template_updated",
                    "name": name,
                    "language": language
                }
                
                message = aio_pika.Message(
                    body=json.dumps(message_body).encode(),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT # Make message durable
                )
                
                # Publish to the exchange (no routing key needed for fanout)
                await exchange.publish(message, routing_key="")
                logger.info(f"Published invalidation message for: {name}:{language}")
                
            except Exception as e:
                logger.error(f"Failed to publish message: {e}")

# Create a single instance to be used by the app
messaging_service = MessagingService(RABBITMQ_URL)