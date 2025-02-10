# stdlib
from datetime import datetime
from typing import Any
from uuid import UUID

# thirdparty
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

# project
from models import ScheduledNotification
from repositories.sql.base import BaseCRUDRepository
from repositories.sql.interfaces.repositories import (
    IScheduledNotificationRepository,
)


class ScheduledNotificationRepository(
    BaseCRUDRepository[ScheduledNotification, Any, Any],
    IScheduledNotificationRepository[ScheduledNotification, Any, Any],
):
    """Репозиторий для работы с запланированными уведомлениями."""

    def __init__(self, session: AsyncSession):
        super().__init__(ScheduledNotification, session)

    async def get_pending(self, current_time: datetime, limit: int | None = None) -> list[ScheduledNotification]:
        """Получает список уведомлений, готовых к отправке."""
        query = (
            select(self.model)
            .where(
                and_(
                    self.model.is_sent.is_(False),
                    self.model.scheduled_time <= current_time,
                )
            )
            .order_by(self.model.scheduled_time)
        )

        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_ids(self, ids: list[UUID]) -> list[ScheduledNotification]:
        """Получает список уведомлений по их ID."""
        query = select(self.model).where(
            and_(
                self.model.id.in_(ids),
                self.model.is_sent.is_(False),
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
