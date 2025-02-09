# stdlib
from datetime import datetime
from uuid import UUID

# thirdparty
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

# project
from src.domain.interfaces.repositories import IScheduledNotificationRepository
from src.models import ScheduledNotification
from src.repositories.sql.base import BaseCRUDRepository


class ScheduledNotificationRepository(
    BaseCRUDRepository[ScheduledNotification], IScheduledNotificationRepository[ScheduledNotification]
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
                    self.model.next_retry_time.is_(None),
                    self.model.retry_count < self.model.max_retries,
                )
            )
            .order_by(self.model.scheduled_time)
        )

        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending_retries(
        self, current_time: datetime, limit: int | None = None
    ) -> list[ScheduledNotification]:
        """Получает список уведомлений для повторной отправки."""
        query = (
            select(self.model)
            .where(
                and_(
                    self.model.is_sent.is_(False),
                    self.model.next_retry_time <= current_time,
                    self.model.retry_count < self.model.max_retries,
                )
            )
            .order_by(self.model.next_retry_time)
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
                self.model.retry_count < self.model.max_retries,
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
