"""
API module for the Template Service.

This module contains all API routes and is responsible for routing
requests to the appropriate endpoints.
"""

from .routes import router

__all__ = ["router"]
