"""
Logging configuration and utilities
"""
import logging
import sys
from typing import Any, Dict
from app.core.config import settings


def setup_logging() -> None:
    """Setup application logging configuration"""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("redis").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance with specified name"""
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to services"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger instance for this class"""
        return get_logger(self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message with optional extra data"""
        self.logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with optional extra data"""
        self.logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, error: Exception = None, **kwargs: Any) -> None:
        """Log error message with optional exception and extra data"""
        extra_data = kwargs.copy()
        if error:
            extra_data['error'] = str(error)
            extra_data['error_type'] = type(error).__name__
        
        self.logger.error(message, extra=extra_data, exc_info=error)
    
    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with optional extra data"""
        self.logger.debug(message, extra=kwargs)


# Initialize logging
setup_logging()