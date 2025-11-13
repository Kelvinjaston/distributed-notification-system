"""
Retry logic with exponential backoff.
"""
import asyncio
import logging
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: int = 1,
    max_delay: int = 60,
    *args,
    **kwargs
) -> Any:
    """
    Execute function with exponential backoff retry logic.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Function result or raises last exception
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            if attempt == max_retries:
                logger.error(
                    f"{func.__name__} failed after {max_retries + 1} attempts: {str(e)}"
                )
                raise

            # Calculate exponential backoff delay
            delay = min(base_delay * (2 ** attempt), max_delay)
            logger.warning(
                f"{func.__name__} attempt {attempt + 1} failed: {str(e)}. "
                f"Retrying in {delay}s..."
            )
            await asyncio.sleep(delay)

    raise last_exception


def async_retry(
    max_retries: int = 3,
    base_delay: int = 1,
    max_delay: int = 60
):
    """Decorator for async retry with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(
                lambda: func(*args, **kwargs),
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay
            )
        return wrapper
    return decorator
