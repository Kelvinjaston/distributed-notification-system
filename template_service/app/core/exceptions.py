"""
Custom exceptions for the Template Service.
"""
from typing import Optional, Any, Dict


class TemplateServiceException(Exception):
    """Base exception for Template Service."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class TemplateNotFoundError(TemplateServiceException):
    """Raised when a template is not found."""

    def __init__(self, message: str = "Template not found", details: Optional[Dict] = None):
        super().__init__(message, status_code=404, details=details)


class TemplateDuplicateError(TemplateServiceException):
    """Raised when attempting to create a duplicate template."""

    def __init__(self, message: str = "Template already exists", details: Optional[Dict] = None):
        super().__init__(message, status_code=409, details=details)


class InvalidTemplateError(TemplateServiceException):
    """Raised when template data is invalid."""

    def __init__(self, message: str = "Invalid template data", details: Optional[Dict] = None):
        super().__init__(message, status_code=400, details=details)


class VariableSubstitutionError(TemplateServiceException):
    """Raised when variable substitution fails."""

    def __init__(self, message: str = "Variable substitution failed", details: Optional[Dict] = None):
        super().__init__(message, status_code=400, details=details)


class CacheError(TemplateServiceException):
    """Raised when cache operation fails."""

    def __init__(self, message: str = "Cache operation failed", details: Optional[Dict] = None):
        super().__init__(message, status_code=503, details=details)


class MessagingError(TemplateServiceException):
    """Raised when messaging operation fails."""

    def __init__(self, message: str = "Messaging operation failed", details: Optional[Dict] = None):
        super().__init__(message, status_code=503, details=details)


class DatabaseError(TemplateServiceException):
    """Raised when database operation fails."""

    def __init__(self, message: str = "Database operation failed", details: Optional[Dict] = None):
        super().__init__(message, status_code=503, details=details)


class ValidationError(TemplateServiceException):
    """Raised when validation fails."""

    def __init__(self, message: str = "Validation failed", details: Optional[Dict] = None):
        super().__init__(message, status_code=422, details=details)


class CircuitBreakerOpenError(TemplateServiceException):
    """Raised when circuit breaker is open."""

    def __init__(self, message: str = "Service temporarily unavailable", details: Optional[Dict] = None):
        super().__init__(message, status_code=503, details=details)
