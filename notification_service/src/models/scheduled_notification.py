# stdlib
from datetime import datetime
from uuid import UUID

# thirdparty
from domain.enums import NotificationType
from sqlalchemy import JSON, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

# project
from models.base import Base


class ScheduledNotification(Base):
    """Модель запланированного уведомления."""

    staff_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    subscribers: Mapped[list[UUID]] = mapped_column(ARRAY(PG_UUID(as_uuid=True)), nullable=False)
    template_id: Mapped[UUID] = mapped_column(ForeignKey("template.id"), nullable=False)
    notification_type: Mapped[NotificationType] = mapped_column(nullable=False)
    scheduled_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_sent: Mapped[bool] = mapped_column(default=False)
    context: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Индексы для оптимизации запросов
    __table_args__ = (
        # Для поиска неотправленных уведомлений с ближайшим временем отправки
        Index(
            "ix_scheduled_notifications_pending",
            is_sent,
            scheduled_time,
            postgresql_where=is_sent.is_(False),
        ),
        # Для быстрого поиска уведомлений пользователя
        Index(
            "ix_scheduled_notifications_user",
            subscribers,
            scheduled_time.desc(),
        ),
    )
