"""
Dependency injection providers for the Template Service.

This module defines FastAPI dependencies that are used to inject
database sessions, cache connections, and message queue channels
into route handlers.
"""

from fastapi import HTTPException, Request
from redis.asyncio import Redis
from aio_pika.channel import Channel
from app.database import get_session  # Re-export database session

__all__ = ["get_session", "get_redis", "get_rabbit_channel"]


async def get_redis(request: Request) -> Redis:
    """
    Dependency to get the Redis connection from app state.

    Raises:
        HTTPException: If Redis is not available
    """
    if not hasattr(request.app.state, "redis") or not request.app.state.redis:
        raise HTTPException(
            status_code=503,
            detail="Redis connection not available."
        )
    return request.app.state.redis


async def get_rabbit_channel(request: Request) -> Channel:
    """
    Dependency to get the RabbitMQ channel from app state.

    Raises:
        HTTPException: If RabbitMQ is not available
    """
    if not hasattr(request.app.state, "rabbit_channel") or not request.app.state.rabbit_channel:
        raise HTTPException(
            status_code=503,
            detail="RabbitMQ connection not available."
        )
    return request.app.state.rabbit_channel

