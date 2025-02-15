# stdlib
from typing import Annotated
from uuid import UUID

# thirdparty
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

# project
from api.v1.pagination import PaginationParams
from db.db import get_session
from repositories.sql.scheduled_notification import (
    ScheduledNotificationRepository,
)
from schemas.scheduled_notifications import (
    ScheduledNotificationCreate,
    ScheduledNotificationResponse,
    ScheduledNotificationUpdate,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ScheduledNotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_scheduled_notification(
    notification: ScheduledNotificationCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> ScheduledNotificationResponse:
    repo = ScheduledNotificationRepository(db)
    try:
        db_notification = await repo.create(obj_in=notification)
        return ScheduledNotificationResponse.model_validate(db_notification)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{notification_id}",
    response_model=ScheduledNotificationResponse,
)
async def get_scheduled_notification(
    notification_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> ScheduledNotificationResponse:
    repo = ScheduledNotificationRepository(db)
    db_notification = await repo.get(notification_id)
    if db_notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled notification not found",
        )
    return ScheduledNotificationResponse.model_validate(db_notification)


@router.put(
    "/{notification_id}",
    response_model=ScheduledNotificationResponse,
)
async def update_scheduled_notification(
    notification_id: UUID,
    notification: ScheduledNotificationUpdate,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> ScheduledNotificationResponse:
    repo = ScheduledNotificationRepository(db)
    db_notification = await repo.get(notification_id)
    if db_notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled notification not found",
        )
    db_notification = await repo.update(db_obj=db_notification, obj_in=notification)
    return ScheduledNotificationResponse.model_validate(db_notification)


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_scheduled_notification(
    notification_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    repo = ScheduledNotificationRepository(db)
    db_notification = await repo.delete(notification_id)
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled notification not found",
        )


@router.get(
    "/",
    response_model=list[ScheduledNotificationResponse],
)
async def get_all_scheduled_notifications(
    pagination_params: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> list[ScheduledNotificationResponse]:
    repo = ScheduledNotificationRepository(db)
    notifications = await repo.get_multi(
        skip=(pagination_params.page_number - 1) * pagination_params.page_size,
        limit=pagination_params.page_size,
    )
    return [ScheduledNotificationResponse.model_validate(db_notification) for db_notification in notifications]
