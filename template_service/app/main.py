"""
Main FastAPI application entry point for the Template Service.

This module configures the FastAPI app with:
- Lifespan management (startup/shutdown)
- Redis and RabbitMQ initialization
- API route registration
- Exception handlers
- Health check endpoints
"""

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from contextlib import asynccontextmanager
import logging

from app.database import create_db_and_tables, close_db_connection
from app.schemas import BaseResponse
from app.dependencies import get_redis, get_rabbit_channel
from app.api import router as api_router
from services.cache import cache_service
from services.messaging import messaging_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle application startup and shutdown events.
    """
    logger.info("Starting up Template Service...")
    try:
        # On startup: Create database tables
        await create_db_and_tables()
        logger.info("Database tables created (if not exist).")

        # Initialize Redis and RabbitMQ connection pools
        await cache_service.init_redis_pool()
        await messaging_service.init_rabbitmq_connection()

        # Store connections in app.state for dependencies
        app.state.redis = await cache_service.get_connection()
        app.state.rabbit_channel = await messaging_service.get_channel()

    except Exception as e:
        logger.error(f"Failed during startup: {e}")

    yield  # The application is now running

    # On shutdown:
    logger.info("Shutting down Template Service...")
    if hasattr(app.state, "redis") and app.state.redis:
        await app.state.redis.close()
    if hasattr(app.state, "rabbit_channel") and app.state.rabbit_channel:
        await app.state.rabbit_channel.close()

    await close_db_connection()
    await cache_service.close_redis_pool()
    await messaging_service.close_rabbitmq_connection()
    logger.info("Shutdown complete.")


# Initialize the FastAPI app with the lifespan event handler
app = FastAPI(
    title="Template Service",
    description="Manages email and push notification templates for the HNG Distributed Notification System.",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Custom Exception Handler ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(
            success=False,
            message="An error occurred.",
            error=exc.detail,
        ).model_dump(),
    )


# --- Include the API Routes ---
app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/health", response_model=BaseResponse, tags=["Monitoring"])
async def health_check():
    """
    Health check endpoint required by the HNG spec.
    """
    return BaseResponse(
        success=True,
        message="Template Service is healthy and running.",
    )
