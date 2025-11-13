from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List
from datetime import datetime
import enum

# This TypeVar is used to create a generic response model.
T = TypeVar('T')

# --- HNG Required Shared Models ---

class PaginationMeta(BaseModel):
    """
    Pydantic model for pagination metadata, matching the HNG spec.
    """
    total: int
    limit: int
    page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class BaseResponse(BaseModel, Generic[T]):
    """
    The standard response format required by the HNG spec.
    All API endpoints should return this model.
    """
    success: bool = True
    message: str
    data: Optional[T] = None
    error: Optional[str] = None
    meta: Optional[PaginationMeta] = None

# --- Template-Specific Enums and Schemas ---

class TemplateType(str, enum.Enum):
    """
    Enum for template types, mirroring the one in models.py
    for Pydantic validation.
    """
    EMAIL = "email"
    PUSH = "push"


class TemplateBase(BaseModel):
    """
    Base schema for a template, containing common fields.
    All field names are snake_case as required.
    """
    name: str
    type: TemplateType
    language: str = "en"
    subject: Optional[str] = None
    body: str

    class Config:
        # This allows Pydantic to read data from ORM models
        from_attributes = True


class TemplateCreate(TemplateBase):
    """
    Schema used for creating a new template (POST /templates).
    """
    pass # Inherits all fields from TemplateBase


class TemplatePublic(TemplateBase):
    """
    Schema for data returned to the user (the public response).
    Includes fields from the database model like id, version, etc.
    """
    id: int
    version: int
    created_at: datetime
    updated_at: datetime


class TemplateUpdate(BaseModel):
    """
    Schema for updating an existing template (PUT /templates/{name}).
    All fields are optional for partial updates.
    """
    subject: Optional[str] = None
    body: Optional[str] = None