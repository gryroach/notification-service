# stdlib
from datetime import datetime
from uuid import UUID

# thirdparty
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

# project
from models import PeriodicNotification
from repositories.sql.base import BaseCRUDRepository
from repositories.sql.interfaces.repositories import (
    IPeriodicNotificationRepository,
)
from schemas.periodic_notifications import (
    PeriodicNotificationCreate,
    PeriodicNotificationUpdate,
)


class PeriodicNotificationRepository(
    BaseCRUDRepository[PeriodicNotification, PeriodicNotificationCreate, PeriodicNotificationUpdate],
    IPeriodicNotificationRepository[PeriodicNotification, PeriodicNotificationCreate, PeriodicNotificationUpdate],
):
    """Репозиторий для работы с периодическими уведомлениями."""

    def __init__(self, session: AsyncSession):
        super().__init__(PeriodicNotification, session)

    async def update_active_status(self, current_time: datetime) -> None:
        """Обновляет статус is_active на основе stop_date."""
        await self.session.execute(
            update(self.model)
            .where(
                and_(
                    self.model.is_active.is_(True),
                    self.model.stop_date <= current_time,
                )
            )
            .values(is_active=False)
        )
        await self.session.commit()

    async def get_pending(self, current_time: datetime, limit: int | None = None) -> list[PeriodicNotification]:
        """Получает список уведомлений, готовых к отправке."""
        await self.update_active_status(current_time)

        query = (
            select(self.model)
            .where(
                and_(
                    self.model.is_active.is_(True),
                    self.model.next_run_time <= current_time,
                )
            )
            .order_by(self.model.next_run_time)
        )

        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_ids(self, ids: list[UUID]) -> list[PeriodicNotification]:
        """Получает список уведомлений по их ID."""
        query = select(self.model).where(
            and_(
                self.model.id.in_(ids),
                self.model.is_active.is_(True),
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active(self) -> list[PeriodicNotification]:
        """Получает список активных периодических уведомлений."""
        query = select(self.model).where(self.model.is_active.is_(True))
        result = await self.session.execute(query)
        return list(result.scalars().all())
