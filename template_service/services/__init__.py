"""
Services module for the Template Service.

This module contains all external service integrations including:
- Redis cache service
- RabbitMQ messaging service
"""

from services.cache import cache_service
from services.messaging import messaging_service

__all__ = ["cache_service", "messaging_service"]
