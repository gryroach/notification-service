# stdlib
from datetime import datetime
from uuid import UUID

# thirdparty
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

# project
from src.domain.interfaces.repositories import IPeriodicNotificationRepository
from src.models import PeriodicNotification
from src.repositories.sql.base import BaseCRUDRepository


class PeriodicNotificationRepository(
    BaseCRUDRepository[PeriodicNotification], IPeriodicNotificationRepository[PeriodicNotification]
):
    """Репозиторий для работы с периодическими уведомлениями."""

    def __init__(self, session: AsyncSession):
        super().__init__(PeriodicNotification, session)

    async def get_pending(self, current_time: datetime, limit: int | None = None) -> list[PeriodicNotification]:
        """Получает список уведомлений, готовых к отправке."""
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
