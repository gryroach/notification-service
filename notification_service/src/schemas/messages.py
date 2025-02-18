# stdlib
from uuid import UUID

# thirdparty
from pydantic import BaseModel

# project
from enums.db import ChannelType, EventType
from enums.rabbitmq import MessageType


class Message(BaseModel):
    event_type: EventType
    channel_type: ChannelType = ChannelType.EMAIL
    template_id: UUID
    context: dict
    subscribers: list[UUID]


class MessageResponse(BaseModel):
    status: str
    message: str
    queue: str
    priority: int
    x_request_id: str | None


class RabbitMQMessage(BaseModel):
    template_id: str
    context: dict
    subscribers: list[str]
    event_type: EventType
    channel_type: ChannelType
    notification_id: str | None
    message_type: MessageType
