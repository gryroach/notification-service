# stdlib
from datetime import UTC, datetime
from typing import Self
from uuid import UUID

# thirdparty
from croniter import CroniterBadCronError, croniter
from pydantic import BaseModel, field_validator, model_validator

# project
from enums import ChannelType, EventType
from enums.subscriber_enum import SubscriberQueryEnum


class PeriodicNotificationInput(BaseModel):
    subscriber_query_type: SubscriberQueryEnum
    subscriber_query_params: dict | None
    template_id: UUID
    channel_type: ChannelType
    event_type: EventType = EventType.CUSTOM
    cron_schedule: str
    last_run_time: datetime | None = None
    next_run_time: datetime | None = None
    is_active: bool = True
    context: dict | None = None
    stop_date: datetime | None = None

    @field_validator("cron_schedule")
    @classmethod
    def cron_schedule_validate(cls, v: str) -> str:
        try:
            croniter(v)
        except CroniterBadCronError:
            raise ValueError("Invalid cron schedule string")
        return v

    @model_validator(mode="after")
    def check_dates(self) -> Self:
        if self.next_run_time is None:
            self.next_run_time = croniter(self.cron_schedule).get_next(datetime).astimezone(UTC)
        elif self.stop_date and self.next_run_time > self.stop_date:
            raise ValueError("Invalid next run time")
        if self.stop_date and self.stop_date < datetime.now(UTC):
            self.is_active = False
        return self


class PeriodicNotificationCreate(PeriodicNotificationInput):
    staff_id: UUID


class PeriodicNotificationUpdate(PeriodicNotificationCreate):
    pass


class PeriodicNotificationResponse(BaseModel):
    id: UUID
    staff_id: UUID
    subscriber_query_type: str
    subscriber_query_params: dict | None
    template_id: UUID
    channel_type: ChannelType
    event_type: EventType
    cron_schedule: str
    last_run_time: datetime | None = None
    next_run_time: datetime
    is_active: bool
    context: dict | None = None
    stop_date: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
