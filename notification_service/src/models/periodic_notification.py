# stdlib
from datetime import UTC, datetime
from uuid import UUID

# thirdparty
from croniter import croniter
from sqlalchemy import ARRAY, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

# project
from src.domain.enums import NotificationType
from src.models.base import Base


class PeriodicNotification(Base):
    """Модель периодического уведомления."""

    staff_id: Mapped[UUID] = mapped_column(String(36), nullable=False)
    subscribers: Mapped[list[UUID]] = mapped_column(ARRAY(String(36)), nullable=False)
    template_id: Mapped[UUID] = mapped_column(ForeignKey("template.id"), nullable=False)
    notification_type: Mapped[NotificationType] = mapped_column(nullable=False)
    cron_schedule: Mapped[str] = mapped_column(String(100), nullable=False)
    last_run_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_run_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    context: Mapped[dict] = mapped_column(Text, nullable=True)
    stop_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Индексы для оптимизации запросов
    __table_args__ = (
        # Для поиска активных уведомлений с ближайшим временем выполнения
        Index(
            "ix_periodic_notifications_active_next_run",
            is_active,
            next_run_time,
            postgresql_where=is_active.is_(True),
        ),
        # Для поиска по пользователю
        Index("ix_periodic_notifications_user", subscribers),
    )

    def calculate_next_run(self, from_time: datetime | None = None) -> datetime:
        """Вычисляет время следующего запуска на основе CRON-расписания."""
        base_time = from_time or self.last_run_time or datetime.now(UTC)
        cron = croniter(self.cron_schedule, base_time)
        return cron.get_next(datetime)
