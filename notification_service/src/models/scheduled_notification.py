# stdlib
from datetime import datetime
from uuid import UUID

# thirdparty
from sqlalchemy import JSON, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

# project
from enums import ChannelType
from enums.db import EventType
from models.base import Base


class ScheduledNotification(Base):
    """Модель запланированного уведомления."""

    staff_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    template_id: Mapped[UUID] = mapped_column(ForeignKey("template.id"), nullable=False)
    channel_type: Mapped[ChannelType] = mapped_column(nullable=False)
    event_type: Mapped[EventType] = mapped_column(nullable=False)
    scheduled_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_sent: Mapped[bool] = mapped_column(default=False)
    context: Mapped[dict] = mapped_column(JSON, nullable=True)
    subscriber_query_type: Mapped[str] = mapped_column(String(50), nullable=False)
    subscriber_query_params: Mapped[dict] = mapped_column(JSON, nullable=True)

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
            "ix_scheduled_notifications_query_type",
            subscriber_query_type,
            scheduled_time.desc(),
        ),
    )
