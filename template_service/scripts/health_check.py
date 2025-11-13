#!/usr/bin/env python
"""
Health check script for Template Service.
Can be used in health check endpoints and monitoring.
"""
import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthChecker:
    """Health check for the template service."""

    def __init__(self):
        self.health_status = {
            "timestamp": datetime.now().isoformat(),
            "service": "Template Service",
            "status": "healthy",
            "checks": {}
        }

    async def check_database(self) -> bool:
        """Check database connectivity."""
        try:
            from app.database import engine
            from sqlalchemy import text

            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            self.health_status["checks"]["database"] = {"status": "up"}
            return True
        except Exception as e:
            self.health_status["checks"]["database"] = {
                "status": "down",
                "error": str(e)
            }
            return False

    async def check_redis(self) -> bool:
        """Check Redis connectivity."""
        try:
            from services.cache import cache_service
            redis = await cache_service.get_connection()
            await redis.ping()
            self.health_status["checks"]["redis"] = {"status": "up"}
            return True
        except Exception as e:
            self.health_status["checks"]["redis"] = {
                "status": "down",
                "error": str(e)
            }
            return False

    async def check_rabbitmq(self) -> bool:
        """Check RabbitMQ connectivity."""
        try:
            from services.messaging import messaging_service
            channel = await messaging_service.get_channel()
            self.health_status["checks"]["rabbitmq"] = {"status": "up"}
            return True
        except Exception as e:
            self.health_status["checks"]["rabbitmq"] = {
                "status": "down",
                "error": str(e)
            }
            return False

    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_rabbitmq(),
            return_exceptions=True
        )

        # Determine overall status
        if all(isinstance(r, bool) and r for r in results):
            self.health_status["status"] = "healthy"
        else:
            self.health_status["status"] = "unhealthy"

        return self.health_status


async def main():
    """Run health check."""
    checker = HealthChecker()
    status = await checker.run_all_checks()

    print(json.dumps(status, indent=2))

    # Return exit code based on status
    return 0 if status["status"] == "healthy" else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
