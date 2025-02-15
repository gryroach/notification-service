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
from repositories.sql.periodic_notification import (
    PeriodicNotificationRepository,
)
from schemas.auth import JwtToken
from schemas.periodic_notifications import (
    PeriodicNotificationCreate,
    PeriodicNotificationInput,
    PeriodicNotificationResponse,
    PeriodicNotificationUpdate,
)
from services.jwt_token import JWTBearer

router = APIRouter()


@router.post(
    "/",
    response_model=PeriodicNotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_periodic_notification(
    notification: PeriodicNotificationInput,
    db: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[JwtToken, Depends(JWTBearer())],
) -> PeriodicNotificationResponse:
    repo = PeriodicNotificationRepository(db)
    db_notification = await repo.create(
        obj_in=PeriodicNotificationCreate(**notification.model_dump(), staff_id=token_payload.user)
    )
    return PeriodicNotificationResponse.model_validate(db_notification)


@router.get(
    "/{notification_id}",
    response_model=PeriodicNotificationResponse,
    dependencies=[Depends(JWTBearer())],
)
async def get_periodic_notification(
    notification_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> PeriodicNotificationResponse:
    repo = PeriodicNotificationRepository(db)
    db_notification = await repo.get(notification_id)
    if db_notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Periodic notification not found",
        )
    return PeriodicNotificationResponse.model_validate(db_notification)


@router.put(
    "/{notification_id}",
    response_model=PeriodicNotificationResponse,
)
async def update_periodic_notification(
    notification_id: UUID,
    notification: PeriodicNotificationInput,
    db: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[JwtToken, Depends(JWTBearer())],
) -> PeriodicNotificationResponse:
    repo = PeriodicNotificationRepository(db)
    db_notification = await repo.get(notification_id)
    if db_notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Periodic notification not found",
        )
    db_notification = await repo.update(
        db_obj=db_notification,
        obj_in=PeriodicNotificationUpdate(**notification.model_dump(), staff_id=token_payload.user),
    )
    return PeriodicNotificationResponse.model_validate(db_notification)


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(JWTBearer())],
)
async def delete_periodic_notification(
    notification_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    repo = PeriodicNotificationRepository(db)
    db_notification = await repo.delete(notification_id)
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Periodic notification not found",
        )


@router.get(
    "/",
    response_model=list[PeriodicNotificationResponse],
    dependencies=[Depends(JWTBearer())],
)
async def get_all_periodic_notifications(
    pagination_params: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> list[PeriodicNotificationResponse]:
    repo = PeriodicNotificationRepository(db)
    notifications = await repo.get_multi(
        skip=(pagination_params.page_number - 1) * pagination_params.page_size,
        limit=pagination_params.page_size,
    )
    return [PeriodicNotificationResponse.model_validate(db_notification) for db_notification in notifications]
