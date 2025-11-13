"""
Correlation ID tracking for distributed tracing.
"""
import uuid
from typing import Optional
from contextvars import ContextVar

correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default=None)


def get_correlation_id() -> str:
    """Get current correlation ID or generate new one."""
    correlation_id = correlation_id_var.get()
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
        correlation_id_var.set(correlation_id)
    return correlation_id


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID."""
    correlation_id_var.set(correlation_id)


def generate_correlation_id() -> str:
    """Generate new correlation ID."""
    return str(uuid.uuid4())
