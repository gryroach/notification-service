# stdlib
from datetime import datetime
from uuid import UUID

# thirdparty
from pydantic import BaseModel

# project
from enums import ChannelType, EventType
from enums.subscriber_enum import SubscriberQueryEnum


class ScheduledNotificationInput(BaseModel):
    subscriber_query_type: SubscriberQueryEnum
    subscriber_query_params: dict | None
    template_id: UUID
    channel_type: ChannelType
    event_type: EventType = EventType.CUSTOM
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
    subscriber_query_type: str
    subscriber_query_params: dict | None
    template_id: UUID
    channel_type: ChannelType
    event_type: EventType
    scheduled_time: datetime
    is_sent: bool
    context: dict | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
