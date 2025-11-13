#!/usr/bin/env python
"""
Database migration script.
Creates or updates database schema.
"""
import asyncio
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    """Initialize database with tables."""
    try:
        from app.database import create_db_and_tables

        logger.info("Creating database tables...")
        await create_db_and_tables()
        logger.info("✓ Database initialized successfully")
        return 0
    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {str(e)}")
        return 1


async def main():
    """Run migrations."""
    logger.info("=== Database Migration ===")
    return await init_db()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
