import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, func, Index, Enum
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

# We define the Enum here for the database
class TemplateTypeDB(str, enum.Enum):
    EMAIL = "email"
    PUSH = "push"

class Template(Base):
    """
    SQLAlchemy model for the 'templates' table in PostgreSQL.
    """
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(TemplateTypeDB), nullable=False)
    language = Column(String(10), nullable=False, default="en")
    subject = Column(String(255), nullable=True)
    body = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_name_lang_version', 'name', 'language', 'version', unique=True),
    )

    def __repr__(self):
        return f"<Template(name='{self.name}', lang='{self.language}', v{self.version})>"