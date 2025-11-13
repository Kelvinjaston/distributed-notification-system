"""
Application constants.
"""

# Template Status
class TemplateStatus:
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"

    ALL = [DRAFT, PUBLISHED, ARCHIVED, DEPRECATED]


# Notification Types
class NotificationType:
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"

    ALL = [EMAIL, PUSH, SMS]


# Template Languages
class Language:
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ARABIC = "ar"
    CHINESE = "zh"
    PORTUGUESE = "pt"

    ALL = [ENGLISH, SPANISH, FRENCH, GERMAN, ARABIC, CHINESE, PORTUGUESE]


# Cache Keys
class CacheKeys:
    TEMPLATE = "template:{name}:{language}:{version}"
    TEMPLATE_LATEST = "template_latest:{name}:{language}"
    TEMPLATE_ALL = "templates:all:{page}:{limit}"
    TEMPLATE_COUNT = "templates:count"

    # Rate limiting
    RATE_LIMIT = "rate_limit:{client_id}:{window}"


# Queue Names
class QueueNames:
    TEMPLATE_QUEUE = "template.queue"
    TEMPLATE_DLQ = "template.dlq"
    TEMPLATE_UPDATE = "template.update"
    TEMPLATE_DELETE = "template.delete"


# Error Codes
class ErrorCodes:
    TEMPLATE_NOT_FOUND = "TEMPLATE_NOT_FOUND"
    TEMPLATE_DUPLICATE = "TEMPLATE_DUPLICATE"
    INVALID_TEMPLATE = "INVALID_TEMPLATE"
    VARIABLE_SUBSTITUTION_ERROR = "VARIABLE_SUBSTITUTION_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    MESSAGING_ERROR = "MESSAGING_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CIRCUIT_BREAKER_OPEN = "CIRCUIT_BREAKER_OPEN"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


# Response Messages
class ResponseMessages:
    SUCCESS = "Operation successful"
    TEMPLATE_CREATED = "Template created successfully"
    TEMPLATE_UPDATED = "Template updated successfully"
    TEMPLATE_DELETED = "Template deleted successfully"
    TEMPLATE_RETRIEVED = "Template retrieved successfully"
    ERROR = "An error occurred"
    INVALID_REQUEST = "Invalid request"
    UNAUTHORIZED = "Unauthorized"
    NOT_FOUND = "Resource not found"
    CONFLICT = "Resource already exists"
    SERVICE_UNAVAILABLE = "Service temporarily unavailable"
