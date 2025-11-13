"""
Database configuration and session management for the Template Service.

This module handles:
- AsyncSQL database engine creation
- Async session factory setup
- Database initialization on startup
- Proper cleanup on shutdown
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Base

# Database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db/template_db")

# Create the async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (development)
    future=True
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_session() -> AsyncSession:
    """
    Dependency to get an async database session.
    Ensures the session is always closed.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_db_and_tables():
    """
    Initializes the database and creates tables on startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db_connection():
    """
    Closes the database connection pool on shutdown.
    """
    await engine.dispose()
