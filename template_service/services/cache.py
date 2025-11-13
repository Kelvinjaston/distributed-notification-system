import redis.asyncio as aioredis
from redis.asyncio.client import Redis
from pydantic import ValidationError
import os
import json
import logging
from typing import Optional
from app.schemas import TemplatePublic # Absolute import

logger = logging.getLogger(__name__)

# This reads from your .env file
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class CacheService:
    """
    Manages the Redis connection pool and all cache-related operations.
    """
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.pool = None

    async def init_redis_pool(self):
        """
        Initializes the Redis connection pool.
        Call this during the FastAPI lifespan startup.
        """
        try:
            self.pool = aioredis.ConnectionPool.from_url(
                self.redis_url, 
                max_connections=20,
                decode_responses=True # Decode from bytes to string
            )
            logger.info("Redis connection pool initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Redis pool: {e}")

    async def close_redis_pool(self):
        """
        Closes the Redis connection pool.
        Call this during the FastAPI lifespan shutdown.
        """
        if self.pool:
            await self.pool.disconnect()
            logger.info("Redis connection pool closed.")

    async def get_connection(self) -> Optional[Redis]:
        """
        Gets a Redis connection from the pool.
        """
        if not self.pool:
            logger.error("Redis pool is not initialized.")
            return None
        return aioredis.Redis(connection_pool=self.pool)

    def _get_template_key(self, name: str, language: str) -> str:
        """
        Generates a consistent key for storing templates in Redis.
        """
        return f"template:{name}:{language}"

    async def get_template_cache(
        self, name: str, language: str
    ) -> Optional[TemplatePublic]:
        """
        Attempts to retrieve a single template from the cache.
        """
        redis = await self.get_connection()
        if not redis:
            return None
            
        key = self._get_template_key(name, language)
        try:
            cached_data = await redis.get(key)
            if cached_data:
                logger.info(f"Cache HIT for key: {key}")
                # Parse the JSON string back into a Pydantic model
                return TemplatePublic.model_validate_json(cached_data)
        except (redis.RedisError, ValidationError, json.JSONDecodeError) as e:
            logger.error(f"Error getting from cache or parsing: {e}")
        
        logger.info(f"Cache MISS for key: {key}")
        return None

    async def set_template_cache(self, template: TemplatePublic, ttl: int = 3600):
        """
        Stores a single template in the cache.
        'ttl' is Time-To-Live in seconds (default 1 hour).
        """
        redis = await self.get_connection()
        if not redis:
            return

        key = self._get_template_key(template.name, template.language)
        try:
            # Serialize the Pydantic model to a JSON string
            await redis.set(key, template.model_dump_json(), ex=ttl)
            logger.info(f"Cache SET for key: {key}")
        except redis.RedisError as e:
            logger.error(f"Error setting cache: {e}")

    async def clear_template_cache(self, name: str, language: str):
        """
        Deletes (invalidates) a template from the cache.
        Called when a template is updated.
        """
        redis = await self.get_connection()
        if not redis:
            return
            
        key = self._get_template_key(name, language)
        try:
            await redis.delete(key)
            logger.info(f"Cache CLEARED for key: {key}")
        except redis.RedisError as e:
            logger.error(f"Error clearing cache: {e}")

# Create a single, shared instance
cache_service = CacheService(REDIS_URL)