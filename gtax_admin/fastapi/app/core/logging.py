"""
Structured logging configuration.

Demonstrates:
- Logging setup with structlog
- Custom processors
- Context managers for logging
- Log level configuration
"""

import logging
import sys
from contextvars import ContextVar
from typing import Any, Optional

import structlog
from structlog.types import Processor

from app.core.config import settings

# Context variable for request-scoped logging context
request_context: ContextVar[dict[str, Any]] = ContextVar("request_context", default={})


def add_request_context(
    logger: logging.Logger,
    method_name: str,
    event_dict: dict[str, Any]
) -> dict[str, Any]:
    """
    Add request context to log entries.
    
    This processor adds request-scoped information like request_id
    to all log entries within a request context.
    
    Args:
        logger: The logger instance
        method_name: The logging method name
        event_dict: The event dictionary to enrich
        
    Returns:
        dict: Enriched event dictionary
    """
    ctx = request_context.get()
    if ctx:
        event_dict.update(ctx)
    return event_dict


def configure_logging() -> None:
    """
    Configure structured logging for the application.
    
    Sets up structlog with appropriate processors based on
    the environment (development vs production).
    """
    # Shared processors for all environments
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        add_request_context,
    ]
    
    if settings.log_format == "json":
        # JSON format for production
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    else:
        # Console format for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Optional logger name, defaults to calling module
        
    Returns:
        BoundLogger: Configured structlog logger
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("User created", user_id=123)
    """
    return structlog.get_logger(name)


class LoggingContext:
    """
    Context manager for adding temporary logging context.
    
    Demonstrates:
    - Context manager protocol (__enter__, __exit__)
    - Temporary state management
    - Proper cleanup on exit
    
    Example:
        >>> with LoggingContext(user_id=123, action="create"):
        ...     logger.info("Processing request")
        # Logs will include user_id and action
    """
    
    def __init__(self, **context: Any) -> None:
        """
        Initialize with context values to add.
        
        Args:
            **context: Key-value pairs to add to logging context
        """
        self._context = context
        self._token: Optional[Any] = None
    
    def __enter__(self) -> "LoggingContext":
        """Enter the context, adding values to request context."""
        current = request_context.get()
        new_context = {**current, **self._context}
        self._token = request_context.set(new_context)
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context, restoring previous state."""
        if self._token is not None:
            request_context.reset(self._token)


# Initialize logging on module import
configure_logging()

# Default logger instance
logger = get_logger("app")
