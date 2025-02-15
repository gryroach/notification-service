# stdlib
from datetime import datetime
from uuid import UUID

# thirdparty
from pydantic import BaseModel

# project
from enums import NotificationType


class ScheduledNotificationInput(BaseModel):
    subscribers: str
    template_id: UUID
    notification_type: NotificationType
    scheduled_time: datetime
    is_sent: bool
    context: dict | None = None


class ScheduledNotificationCreate(ScheduledNotificationInput):
    staff_id: UUID


class ScheduledNotificationUpdate(ScheduledNotificationCreate):
    pass


class ScheduledNotificationResponse(BaseModel):
    id: UUID
    staff_id: UUID
    subscribers: str
    template_id: UUID
    notification_type: NotificationType
    scheduled_time: datetime
    is_sent: bool
    context: dict | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
