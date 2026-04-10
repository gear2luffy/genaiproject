"""
Custom decorators for the application.

Demonstrates:
- Function decorators
- Class decorators
- Decorator with parameters
- Async decorator support
"""

import functools
import time
from typing import Any, Callable, TypeVar, ParamSpec

from app.core.logging import get_logger

logger = get_logger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def log_execution(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to log function execution.
    
    Logs function entry and exit with timing.
    
    Args:
        func: The function to decorate
        
    Returns:
        Callable: Decorated function
        
    Example:
        >>> @log_execution
        ... def my_function(x):
        ...     return x * 2
    """
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        func_name = func.__qualname__
        logger.debug(f"Entering {func_name}")
        
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Exiting {func_name}", duration_ms=round(duration, 2))
            return result
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Error in {func_name}",
                error=str(e),
                duration_ms=round(duration, 2)
            )
            raise
    
    return wrapper


def async_log_execution(func: Callable[P, R]) -> Callable[P, R]:
    """
    Async version of log_execution decorator.
    
    Args:
        func: The async function to decorate
        
    Returns:
        Callable: Decorated async function
    """
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        func_name = func.__qualname__
        logger.debug(f"Entering {func_name}")
        
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Exiting {func_name}", duration_ms=round(duration, 2))
            return result
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Error in {func_name}",
                error=str(e),
                duration_ms=round(duration, 2)
            )
            raise
    
    return wrapper


def retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator factory for retrying failed operations.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay_seconds: Delay between retries
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Callable: Decorator function
        
    Example:
        >>> @retry(max_attempts=3, delay_seconds=1.0)
        ... def unreliable_function():
        ...     ...
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed",
                        function=func.__qualname__,
                        error=str(e)
                    )
                    
                    if attempt < max_attempts:
                        time.sleep(delay_seconds)
            
            raise last_exception
        
        return wrapper
    
    return decorator


def async_retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Async version of retry decorator.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay_seconds: Delay between retries
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Callable: Decorator function
    """
    import asyncio
    
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed",
                        function=func.__qualname__,
                        error=str(e)
                    )
                    
                    if attempt < max_attempts:
                        await asyncio.sleep(delay_seconds)
            
            raise last_exception
        
        return wrapper
    
    return decorator


def cache_result(ttl_seconds: int = 300) -> Callable:
    """
    Simple in-memory cache decorator.
    
    Args:
        ttl_seconds: Time-to-live in seconds
        
    Returns:
        Callable: Decorator function
        
    Note: For production, use Redis or similar caching.
    
    Example:
        >>> @cache_result(ttl_seconds=60)
        ... def expensive_computation(x):
        ...     ...
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        cache: dict[str, tuple[float, Any]] = {}
        
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Create cache key
            key = str((args, tuple(sorted(kwargs.items()))))
            
            # Check cache
            if key in cache:
                cached_time, cached_result = cache[key]
                if time.time() - cached_time < ttl_seconds:
                    logger.debug(
                        "Cache hit",
                        function=func.__qualname__
                    )
                    return cached_result
            
            # Compute and cache
            result = func(*args, **kwargs)
            cache[key] = (time.time(), result)
            
            return result
        
        # Add cache clear method
        wrapper.clear_cache = lambda: cache.clear()
        
        return wrapper
    
    return decorator


def deprecated(reason: str = "") -> Callable:
    """
    Mark a function as deprecated.
    
    Args:
        reason: Reason for deprecation
        
    Returns:
        Callable: Decorator function
        
    Example:
        >>> @deprecated("Use new_function instead")
        ... def old_function():
        ...     ...
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            import warnings
            message = f"{func.__qualname__} is deprecated."
            if reason:
                message += f" {reason}"
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def validate_types(func: Callable[P, R]) -> Callable[P, R]:
    """
    Runtime type validation decorator.
    
    Validates function arguments against type hints at runtime.
    
    Args:
        func: The function to decorate
        
    Returns:
        Callable: Decorated function
    """
    import inspect
    from typing import get_type_hints
    
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        hints = get_type_hints(func)
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        
        for param_name, value in bound.arguments.items():
            if param_name in hints:
                expected_type = hints[param_name]
                # Skip complex types for simplicity
                if hasattr(expected_type, "__origin__"):
                    continue
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"Argument '{param_name}' must be {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
        
        return func(*args, **kwargs)
    
    return wrapper
