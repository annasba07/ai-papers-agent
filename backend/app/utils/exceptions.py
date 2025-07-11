"""
Custom exception classes for the application
"""
from typing import Any, Dict, Optional


class AIDigestException(Exception):
    """Base exception class for AI Paper Digest application"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ServiceException(AIDigestException):
    """Exception raised by service layer"""
    pass


class AIAnalysisException(ServiceException):
    """Exception raised during AI analysis operations"""
    pass


class CacheException(ServiceException):
    """Exception raised during cache operations"""
    pass


class ArxivAPIException(ServiceException):
    """Exception raised during arXiv API operations"""
    pass


class ValidationException(AIDigestException):
    """Exception raised during data validation"""
    pass


class RateLimitException(ServiceException):
    """Exception raised when rate limits are exceeded"""
    pass


class ConfigurationException(AIDigestException):
    """Exception raised for configuration errors"""
    pass