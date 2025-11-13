#!/usr/bin/env python
"""
Debug script for Template Service.
Shows service health, database status, cache status, and message queue status.
"""
import asyncio
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_database_connection():
    """Check database connection."""
    try:
        from app.database import engine
        from sqlalchemy import text

        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection: OK")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection: FAILED - {str(e)}")
        return False


async def check_redis_connection():
    """Check Redis connection."""
    try:
        from services.cache import cache_service
        await cache_service.init_redis_pool()
        redis = await cache_service.get_connection()
        await redis.ping()
        logger.info("✓ Redis connection: OK")
        return True
    except Exception as e:
        logger.error(f"✗ Redis connection: FAILED - {str(e)}")
        return False


async def check_rabbitmq_connection():
    """Check RabbitMQ connection."""
    try:
        from services.messaging import messaging_service
        await messaging_service.init_rabbitmq_connection()
        logger.info("✓ RabbitMQ connection: OK")
        return True
    except Exception as e:
        logger.error(f"✗ RabbitMQ connection: FAILED - {str(e)}")
        return False


async def check_environment():
    """Check environment variables."""
    import os
    required_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "RABBITMQ_URL"
    ]

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        logger.warning(f"✗ Missing environment variables: {', '.join(missing)}")
        return False
    else:
        logger.info("✓ Environment variables: OK")
        return True


async def main():
    """Run all checks."""
    logger.info(f"=== Template Service Debug Report ===")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("")

    # Check environment
    env_ok = await check_environment()

    # Check connections
    db_ok = await check_database_connection()
    redis_ok = await check_redis_connection()
    rabbitmq_ok = await check_rabbitmq_connection()

    logger.info("")
    logger.info("=== Summary ===")
    all_ok = all([env_ok, db_ok, redis_ok, rabbitmq_ok])

    if all_ok:
        logger.info("All systems operational ✓")
        return 0
    else:
        logger.warning("Some systems are not operational")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
