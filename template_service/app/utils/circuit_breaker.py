"""
Circuit Breaker implementation for handling service failures gracefully.
"""
import time
import logging
from enum import Enum
from typing import Callable, Any
from functools import wraps
from app.core.exceptions import CircuitBreakerOpenError

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Service failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        name: str = "CircuitBreaker"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(f"{self.name}: Attempting recovery")
            else:
                raise CircuitBreakerOpenError(
                    f"{self.name}: Circuit breaker is open"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful call."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            logger.info(f"{self.name}: Recovery successful, closing circuit")
            self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        logger.warning(
            f"{self.name}: Failure {self.failure_count}/{self.failure_threshold}"
        )

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.error(f"{self.name}: Circuit breaker opened")

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        return (
            self.last_failure_time is not None
            and (time.time() - self.last_failure_time) >= self.recovery_timeout
        )


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    name: str = None
):
    """Decorator for circuit breaker."""
    def decorator(func: Callable) -> Callable:
        cb = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            name=name or func.__name__
        )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await cb.call(func, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)

        return async_wrapper if "async" in str(func) else sync_wrapper

    return decorator
