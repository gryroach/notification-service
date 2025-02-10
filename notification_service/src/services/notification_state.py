# stdlib
from datetime import UTC, datetime
from uuid import UUID

# thirdparty
from sqlalchemy.ext.asyncio import AsyncSession

# project
from models import PeriodicNotification, ScheduledNotification
from repositories.sql.periodic_notification import (
    PeriodicNotificationRepository,
)
from repositories.sql.scheduled_notification import (
    ScheduledNotificationRepository,
)


class NotificationStateService:
    """Сервис для управления состоянием уведомлений."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.periodic_repo = PeriodicNotificationRepository(session)
        self.scheduled_repo = ScheduledNotificationRepository(session)

    async def get_active_periodic(self) -> list[PeriodicNotification]:
        """Получает список активных периодических уведомлений."""
        return await self.periodic_repo.get_active()

    async def get_pending_periodic(self, current_time: datetime) -> list[PeriodicNotification]:
        """Получает список периодических уведомлений, готовых к отправке."""
        return await self.periodic_repo.get_pending(current_time)

    async def update_periodic_run_time(self, notification_id: UUID, last_run_time: datetime | None = None) -> None:
        """Обновляет время выполнения периодического уведомления."""
        notification = await self.periodic_repo.get(notification_id)
        if not notification:
            return

        next_run_time = notification.calculate_next_run(last_run_time)
        await self.periodic_repo.update(
            db_obj=notification,
            obj_in={
                "last_run_time": last_run_time or datetime.now(UTC),
                "next_run_time": next_run_time,
            },
        )

    async def get_user_periodic(self, user_id: UUID) -> list[PeriodicNotification]:
        """Получает список периодических уведомлений пользователя."""
        return await self.periodic_repo.get_by_field_multi("subscribers", user_id)

    async def get_pending_scheduled(
        self, current_time: datetime, batch_size: int = 100
    ) -> list[ScheduledNotification]:
        """Получает список запланированных уведомлений, готовых к отправке."""
        return await self.scheduled_repo.get_pending(current_time, limit=batch_size)

    async def get_user_scheduled(self, user_id: UUID) -> list[ScheduledNotification]:
        """Получает список запланированных уведомлений пользователя."""
        return await self.scheduled_repo.get_by_field_multi("subscribers", user_id)

    async def mark_scheduled_sent(self, notification_id: UUID) -> None:
        """Отмечает запланированное уведомление как отправленное."""
        notification = await self.scheduled_repo.get(notification_id)
        if not notification:
            return

        await self.scheduled_repo.update(
            db_obj=notification,
            obj_in={"is_sent": True},
        )

    async def update_scheduled_retry(
        self,
        notification_id: UUID,
        next_retry_time: datetime,
        retry_count: int,
    ) -> None:
        """Обновляет данные о повторной отправке запланированного уведомления."""
        notification = await self.scheduled_repo.get(notification_id)
        if not notification:
            return

        await self.scheduled_repo.update(
            db_obj=notification,
            obj_in={
                "next_retry_time": next_retry_time,
                "retry_count": retry_count,
            },
        )
