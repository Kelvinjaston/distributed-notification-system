"""
Template Service Application Module.

This package contains the core application logic for the Template Service,
which is part of the distributed notification system.

The Template Service is responsible for:
- Managing notification templates (email and push)
- Handling template versioning
- Providing template retrieval with caching
- Publishing template update events
"""

from app.main import app

__version__ = "1.0.0"
__all__ = ["app"]
