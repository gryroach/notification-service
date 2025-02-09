# stdlib
from datetime import datetime
from uuid import UUID

# thirdparty
from sqlalchemy import ARRAY, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

# project
from src.domain.enums import NotificationType
from src.models.base import Base


class ScheduledNotification(Base):
    """Модель запланированного уведомления."""

    staff_id: Mapped[UUID] = mapped_column(String(36), nullable=False)
    subscribers: Mapped[list[UUID]] = mapped_column(ARRAY(String(36)), nullable=False)
    template_id: Mapped[UUID] = mapped_column(ForeignKey("template.id"), nullable=False)
    notification_type: Mapped[NotificationType] = mapped_column(nullable=False)
    scheduled_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_sent: Mapped[bool] = mapped_column(default=False)
    context: Mapped[dict] = mapped_column(Text, nullable=True)

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
        Index("ix_scheduled_notifications_user", subscribers, scheduled_time.desc()),
    )
