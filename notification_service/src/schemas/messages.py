# stdlib
from uuid import UUID

# thirdparty
from pydantic import BaseModel

# project
from enums.db import ChannelType, EventType


class Message(BaseModel):
    event_type: EventType
    notification_type: ChannelType = ChannelType.EMAIL
    template_id: UUID
    context: dict
    subscribers: list[UUID]


class MessageResponse(BaseModel):
    status: str
    message: str
    queue: str
    priority: int
    x_request_id: str | None
