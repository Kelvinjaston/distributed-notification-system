from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app import models, schemas  # <-- Use absolute import
from typing import Optional

async def get_template_by_name(
    db: AsyncSession, 
    name: str, 
    language: str = "en"
) -> Optional[models.Template]:
    """
    Fetches the single *latest version* of a template by its name
    and language from the database.
    """
    query = (
        select(models.Template)
        .filter(models.Template.name == name, models.Template.language == language)
        .order_by(desc(models.Template.version))
        .limit(1)
    )
    result = await db.execute(query)
    return result.scalars().first()

async def create_template(
    db: AsyncSession, 
    template: schemas.TemplateCreate
) -> models.Template:
    """
    Creates a new template in the database, starting at version 1.
    """
    # Create the SQLAlchemy model instance from the Pydantic schema
    db_template = models.Template(
        **template.model_dump(),
        version=1  # Always start at version 1
    )
    
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    return db_template

async def create_new_template_version(
    db: AsyncSession, 
    latest_template: models.Template,
    template_update: schemas.TemplateUpdate
) -> models.Template:
    """
    Creates a new version of an existing template by incrementing
    the version number and copying the data.
    """
    # Create a new Template object for the new version
    new_version_template = models.Template(
        name=latest_template.name,
        type=latest_template.type,
        language=latest_template.language,
        # Use new data if provided, else fall back to old data
        subject=template_update.subject if template_update.subject is not None else latest_template.subject,
        body=template_update.body if template_update.body is not None else latest_template.body,
        version=latest_template.version + 1  # Increment the version
    )
    
    db.add(new_version_template)
    await db.commit()
    await db.refresh(new_version_template)
    return new_version_template