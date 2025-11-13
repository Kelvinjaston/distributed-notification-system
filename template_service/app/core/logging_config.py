"""
Logging configuration with support for JSON and text formats.
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger
from app.core.config import settings


class CorrelationIDFilter(logging.Filter):
    """Add correlation ID to logs for request tracing."""

    def filter(self, record: logging.LogRecord) -> bool:
        # This will be set by middleware
        if not hasattr(record, 'correlation_id'):
            record.correlation_id = "N/A"
        return True


def setup_logging() -> None:
    """Configure application logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add correlation filter
    correlation_filter = CorrelationIDFilter()

    if settings.LOG_FORMAT == "json":
        # JSON Logging
        handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            fmt='%(timestamp)s %(level)s %(name)s %(correlation_id)s %(message)s',
            timestamp=True
        )
        handler.setFormatter(formatter)
        handler.addFilter(correlation_filter)
        root_logger.addHandler(handler)
    else:
        # Text Logging
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(correlation_id)s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        handler.addFilter(correlation_filter)
        root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)
