import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from .logging_utils import log_exception

T = TypeVar("T")
P = ParamSpec("P")


def handle_errors(logger: logging.Logger) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to handle and log errors."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_exception(e, logger)
                raise

        return wrapper

    return decorator


def validate_input(
    validator: Callable[[Any], bool], error_msg: str
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to validate input parameters."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if not validator(args[0]):  # Assumes first arg is the input to validate
                raise ValueError(error_msg)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def retry_on_error(
    max_retries: int = 3, delay: float = 1.0, logger: logging.Logger = None
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to retry a function on error."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        if logger:
                            log_exception(e, logger)
                        raise
                    if logger:
                        logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(delay)

        return wrapper

    return decorator
