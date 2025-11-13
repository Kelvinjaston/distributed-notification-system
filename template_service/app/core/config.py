"""
Application configuration settings.
Supports environment-based configuration.
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    APP_NAME: str = "Template Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # Server Settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8082, env="PORT")

    # Service URLs
    USER_SERVICE_URL: Optional[str] = Field(default=None, env="USER_SERVICE_URL")
    TEMPLATE_SERVICE_URL: Optional[str] = Field(default=None, env="TEMPLATE_SERVICE_URL")

    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/template_db",
        env="DATABASE_URL"
    )
    SQLALCHEMY_ECHO: bool = Field(default=True, env="SQLALCHEMY_ECHO")

    # Redis Settings
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    REDIS_CACHE_TTL: int = Field(default=3600, env="REDIS_CACHE_TTL")  # 1 hour

    # RabbitMQ Settings
    RABBITMQ_URL: str = Field(
        default="amqp://guest:guest@localhost:5672/",
        env="RABBITMQ_URL"
    )
    RABBITMQ_EXCHANGE: str = Field(default="notifications.direct", env="RABBITMQ_EXCHANGE")
    RABBITMQ_TEMPLATE_QUEUE: str = Field(default="template.queue", env="RABBITMQ_TEMPLATE_QUEUE")
    RABBITMQ_DLQ: str = Field(default="template.dlq", env="RABBITMQ_DLQ")

    # Retry Settings (Exponential Backoff)
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    RETRY_BASE_DELAY: int = Field(default=1, env="RETRY_BASE_DELAY")  # seconds
    RETRY_MAX_DELAY: int = Field(default=60, env="RETRY_MAX_DELAY")  # seconds

    # Circuit Breaker Settings
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = Field(default=5, env="CIRCUIT_BREAKER_FAILURE_THRESHOLD")
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = Field(default=60, env="CIRCUIT_BREAKER_RECOVERY_TIMEOUT")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "json"  # json or text

    # Security
    API_KEY: Optional[str] = Field(default=None, env="API_KEY")
    USER_SERVICE_API_KEY: Optional[str] = Field(default=None, env="USER_SERVICE_API_KEY")
    JWT_SECRET: Optional[str] = Field(default=None, env="JWT_SECRET")

    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    MAX_PAGE_SIZE: int = Field(default=100, env="MAX_PAGE_SIZE")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=1000, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds

    # Correlation ID
    CORRELATION_ID_HEADER: str = "X-Correlation-ID"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create a singleton instance
settings = Settings()
