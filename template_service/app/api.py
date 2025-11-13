from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio.client import Redis
from aio_pika.channel import Channel
from typing import List

from . import crud, schemas
from .database import get_session
from .dependencies import get_redis, get_rabbit_channel
from services.cache import cache_service
from services.messaging import messaging_service


router = APIRouter()

@router.post(
    "/templates",
    response_model=schemas.BaseResponse[schemas.TemplatePublic],
    status_code=status.HTTP_201_CREATED,
    tags=["Templates"]
)
async def create_template(
    template: schemas.TemplateCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Create a new template.
    
    - Checks if a template with this name already exists.
    - If not, creates it with version 1.
    """
    existing_template = await crud.get_template_by_name(
        db, name=template.name, language=template.language
    )
    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Template with name '{template.name}' and language '{template.language}' already exists."
        )
    
    new_template = await crud.create_template(db=db, template=template)
    
    return schemas.BaseResponse(
        success=True,
        message="Template created successfully.",
        data=new_template
    )

@router.get(
    "/templates/{name}",
    response_model=schemas.BaseResponse[schemas.TemplatePublic],
    status_code=status.HTTP_200_OK,
    tags=["Templates"]
)
async def get_latest_template(
    name: str,
    language: str = "en",
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis) # <-- Add Redis dependency
):
    """
    Get the *latest version* of a template by its unique name.
    
    - Implements Cache-Aside pattern.
    - 1. Check Redis cache.
    - 2. If miss, get from PostgreSQL.
    - 3. After DB fetch, store result in Redis for next time.
    """
    # 1. Check Redis cache
    cached_template = await cache_service.get_template_cache(name, language)
    if cached_template:
        return schemas.BaseResponse(
            success=True,
            message="Template retrieved successfully (from cache).",
            data=cached_template
        )
    
    # 2. If miss, get from PostgreSQL
    template = await crud.get_template_by_name(db, name=name, language=language)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with name '{name}' and language '{language}' not found."
        )
    
    # 3. Store in Redis for next time
    # Convert SQLAlchemy model to Pydantic model for caching
    public_template = schemas.TemplatePublic.model_validate(template)
    await cache_service.set_template_cache(public_template)
        
    return schemas.BaseResponse(
        success=True,
        message="Template retrieved successfully (from database).",
        data=public_template
    )

@router.put(
    "/templates/{name}",
    response_model=schemas.BaseResponse[schemas.TemplatePublic],
    status_code=status.HTTP_200_OK,
    tags=["Templates"]
)
async def update_template(
    name: str,
    template_update: schemas.TemplateUpdate,
    language: str = "en",
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis), # <-- Add Redis
    channel: Channel = Depends(get_rabbit_channel) # <-- Add RabbitMQ
):
    """
    Update a template by creating a new version.
    
    - 1. Finds the latest version in DB.
    - 2. Creates a new version row in DB.
    - 3. Clears the local Redis cache.
    - 4. Publishes an invalidation message to RabbitMQ.
    """
    # 1. Find the latest version
    latest_template = await crud.get_template_by_name(db, name=name, language=language)
    
    if not latest_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with name '{name}' and language '{language}' not found. Cannot update."
        )
    
    # 2. Create a new version
    new_version = await crud.create_new_template_version(
        db=db,
        latest_template=latest_template,
        template_update=template_update
    )
    
    # 3. Clear the local Redis cache
    await cache_service.clear_template_cache(name, language)
    
    # 4. Publish invalidation message to RabbitMQ
    await messaging_service.publish_template_update_message(
        name=name, language=language
    )
    
    return schemas.BaseResponse(
        success=True,
        message=f"Template updated to version {new_version.version} successfully. Cache invalidated.",
        data=new_version
    )